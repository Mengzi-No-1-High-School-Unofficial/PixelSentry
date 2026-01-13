/**
 * 类型定义
 */

export interface SubmitRequest {
    uid: string
    pasteId: string
}

export interface SubmitResponse {
    success: boolean
    submissionId?: number
    message?: string
}

export interface SubmissionStatus {
    id: number
    status: 'pending' | 'processing' | 'success' | 'failed'
    accessKey?: string
    isValid?: boolean
    errorMessage?: string
    createdAt: string
}

export interface AccessKeyInfo {
    id: number
    accessKey: string
    isValid: boolean
    lastValidatedAt: string | null
    validationCount: number
    createdAt: string
}

export interface StatsData {
    totalKeys: number
    validKeys: number
    totalSubmissions: number
    successRate: number
}

export interface LoginRequest {
    username: string
    password: string
}

export interface TokenResponse {
    success: boolean
    accessToken?: string
    refreshToken?: string
    expiresIn?: number
    message?: string
}
