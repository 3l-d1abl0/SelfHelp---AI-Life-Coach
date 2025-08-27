import winston from 'winston';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';

// Ensure logs directory exists
const logsDir = path.resolve('logs');
if (!existsSync(logsDir)) {
	mkdirSync(logsDir, { recursive: true });
}

const logger = winston.createLogger({
	level: 'info',
	format: winston.format.combine(
		winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
		winston.format.printf(({ timestamp, level, message }) => {
			return `[${timestamp}] [${level.toUpperCase()}] ${message}`;
		})
	),
	transports: [
		new winston.transports.File({ 
			filename: path.join(logsDir, 'server.log'),
			maxsize: 5242880, // 5MB
			maxFiles: 5
		}),
		new winston.transports.Console()
	]
});

export default logger;