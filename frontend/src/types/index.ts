export interface Submission {
    id: number
    uid: string
    pasteId: string
    submitterName?: string
    username?: string
    status: 'pending' | 'processing' | 'success' | 'failed'
    loginToken?: string
    accessKey?: string
    errorMessage?: string
    createdAt: string
}

export interface AccessKeyInfo {
    id: number
    accessKey: string
    isValid: boolean
    validationCount: number
    lastValidatedAt?: string
    createdAt: string
    submission?: Submission
}

export interface SubmissionStatus {
    id: number
    status: 'pending' | 'processing' | 'success' | 'failed'
    accessKey?: string
    isValid?: boolean
    errorMessage?: string
    createdAt: string
}

export interface Stats {
    totalKeys: number
    validKeys: number
    totalSubmissions: number
    successRate: number
}

export interface LoginRequest {
    username: string
    password: string
}

export interface LoginResponse {
    accessToken: string
    refreshToken: string
    tokenType: string
}

export interface RefreshRequest {
    refreshToken: string
}

export interface ApiResponse<T = any> {
    success: boolean
    message?: string
    data?: T
    submissionId?: number
}

export interface SubmitRequest {
    uid?: string
    pasteId: string
    submitterName?: string
}

export interface SubmitResponse {
    success: boolean
    message?: string
    submissionId?: number
}
