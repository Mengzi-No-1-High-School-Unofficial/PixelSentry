# PixelSentry 失败重试机制设计文档

## 当前状态

目前系统**不会**自动重试失败的提交。具体行为如下：

### 现有行为

1. **提交失败后**：
   - 状态设置为 `failed`
   - 错误信息记录在 `error_message` 字段
   - 不会自动重试

2. **应用重启后**：
   - 失败的提交保持 `failed` 状态
   - 不会自动重新处理

3. **用户操作**：
   - 用户需要重新提交相同的 UID 和剪贴板 ID
   - 会创建新的提交记录

## 建议的重试机制

### 方案一：启动时自动重试（推荐）

在应用启动时，自动重试所有 `pending` 和 `processing` 状态的提交。

**优点**：
- ✅ 简单可靠
- ✅ 不会丢失因重启导致的未完成任务
- ✅ 不需要额外的调度器

**实现位置**：`app/main.py` 的 `lifespan` 函数

```python
async def retry_pending_submissions():
    """重试所有待处理和处理中的提交"""
    async with AsyncSessionLocal() as db:
        # 查询所有未完成的提交
        result = await db.execute(
            select(Submission).where(
                Submission.status.in_([
                    SubmissionStatus.PENDING,
                    SubmissionStatus.PROCESSING
                ])
            )
        )
        submissions = result.scalars().all()
        
        for submission in submissions:
            # 重置为 pending 状态
            submission.status = SubmissionStatus.PENDING
            submission.error_message = None
            await db.commit()
            
            # 启动后台任务
            asyncio.create_task(
                TokenService.process_submission_with_new_session(submission.id)
            )
```

**配置选项**：
```bash
# .env
AUTO_RETRY_ON_STARTUP=True  # 是否在启动时重试
MAX_RETRY_AGE_HOURS=24      # 只重试 24 小时内的提交
```

---

### 方案二：定时重试机制

使用 APScheduler 定期检查并重试失败的提交。

**优点**：
- ✅ 可以处理临时性错误（如网络问题）
- ✅ 可配置重试次数和间隔

**缺点**：
- ❌ 更复杂
- ❌ 可能重复处理已经永久失败的提交

**实现位置**：`app/main.py`

```python
async def retry_failed_submissions():
    """定时重试失败的提交"""
    async with AsyncSessionLocal() as db:
        # 查询失败且重试次数未超限的提交
        result = await db.execute(
            select(Submission).where(
                Submission.status == SubmissionStatus.FAILED,
                Submission.retry_count < 3  # 最多重试 3 次
            )
        )
        submissions = result.scalars().all()
        
        for submission in submissions:
            submission.retry_count += 1
            submission.status = SubmissionStatus.PENDING
            await db.commit()
            
            asyncio.create_task(
                TokenService.process_submission_with_new_session(submission.id)
            )

# 在 lifespan 中添加
scheduler.add_job(
    retry_failed_submissions,
    "interval",
    hours=1,  # 每小时重试一次
    id="retry_failed",
)
```

**需要的数据库字段**：
```python
# app/models/submission.py
retry_count: Mapped[int] = mapped_column(Integer, default=0)
```

---

### 方案三：手动重试 API

提供管理员 API 手动触发重试。

**优点**：
- ✅ 完全可控
- ✅ 不会浪费资源

**实现位置**：`app/api/admin.py`

```python
@router.post("/retry/{submission_id}")
async def retry_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user),
):
    """手动重试失败的提交"""
    result = await db.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="提交不存在")
    
    if submission.status == SubmissionStatus.SUCCESS:
        raise HTTPException(status_code=400, detail="提交已成功，无需重试")
    
    # 重置状态
    submission.status = SubmissionStatus.PENDING
    submission.error_message = None
    await db.commit()
    
    # 启动后台任务
    asyncio.create_task(
        TokenService.process_submission_with_new_session(submission_id)
    )
    
    return {"success": True, "message": "已启动重试"}
```

---

## 推荐方案

**组合方案：方案一 + 方案三**

1. **启动时自动重试**：处理因重启导致的未完成任务
2. **手动重试 API**：管理员可以手动重试特定的失败提交

### 实现步骤

1. 在 `app/main.py` 添加启动时重试逻辑
2. 在 `app/api/admin.py` 添加手动重试 API
3. 在 `app/services/token_service.py` 添加独立会话的处理方法
4. 在前端管理面板添加"重试"按钮

### 配置文件

```bash
# backend/.env
# 重试配置
AUTO_RETRY_ON_STARTUP=True
MAX_RETRY_AGE_HOURS=24
```

---

## 需要修改的文件

1. **`app/main.py`**：添加启动时重试逻辑
2. **`app/services/token_service.py`**：添加 `process_submission_with_new_session` 方法
3. **`app/api/admin.py`**：添加手动重试 API
4. **`app/config.py`**：添加重试相关配置
5. **`frontend/src/components/KeyItem.vue`**：添加重试按钮
6. **`frontend/src/api/admin.ts`**：添加重试 API 调用

---

## 风险和注意事项

### ⚠️ 潜在问题

1. **重复处理**：如果提交已经部分成功（如已获取 login_token），重试可能导致重复
2. **资源消耗**：大量失败提交重试会消耗 Camoufox 资源
3. **永久失败**：某些错误（如无效的 UID）永远不会成功，不应重试

### 🛡️ 解决方案

1. **幂等性**：确保重试是幂等的，检查是否已有 Access Key
2. **重试限制**：
   - 只重试最近 24 小时的提交
   - 最多重试 3 次
   - 指数退避（第一次立即，第二次 1 小时后，第三次 6 小时后）
3. **错误分类**：
   - 临时错误（网络超时）→ 可重试
   - 永久错误（无效 UID）→ 不重试

---

## 实现优先级

### 高优先级（立即实现）
- ✅ 启动时重试 `pending` 和 `processing` 状态的提交
- ✅ 手动重试 API

### 中优先级（可选）
- ⏸️ 添加 `retry_count` 字段
- ⏸️ 重试次数限制

### 低优先级（未来考虑）
- ⏸️ 定时自动重试
- ⏸️ 指数退避策略
- ⏸️ 错误分类

---

## 总结

**推荐实现**：启动时自动重试 + 手动重试 API

这个方案简单可靠，能够处理大部分场景，同时给管理员足够的控制权。
