import { AuthService } from './auth.service';
declare class LoginDto {
    username: string;
    password: string;
}
export declare class AuthController {
    private authService;
    constructor(authService: AuthService);
    login(loginDto: LoginDto): Promise<{
        access_token: string;
        admin: {
            id: string;
            username: string;
        };
    }>;
    me(req: any): Promise<any>;
}
export {};
