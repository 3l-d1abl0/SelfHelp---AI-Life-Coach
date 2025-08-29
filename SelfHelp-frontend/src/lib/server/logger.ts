import winston from 'winston';
import { existsSync, mkdirSync } from 'fs';
import path from 'path';

// Ensure logs directory exists
const logsDir = path.resolve('logs');
if (!existsSync(logsDir)) {
	mkdirSync(logsDir, { recursive: true });
}


const filenameFormat = winston.format((info) => {
  const stack = new Error().stack;
  if (stack) {
    const stackLines = stack.split('\n');
    const callerLine = stackLines[10] || stackLines[3];
    const match = callerLine.match(/\(([^)]+)\)/);
    if (match) {
      const fullPath = match[1].split(':')[0];
      info.filename = path.basename(fullPath);
    } else {
      info.filename = 'unknown';
    }
  }
  return info;
});

//Set color codes
const customLevels = {
  levels: {
    error: 0,
    warn: 1,
    info: 2,
    debug: 3
  },
  colors: {
    error: 'red',
    warn: 'yellow',
    info: 'green',
    debug: 'blue'
  }
};

//winston.addColors(customLevels.colors);

const logger = winston.createLogger({
	level: 'info',
	format: winston.format.combine(
		filenameFormat(),
		winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.errors({ stack: true }),
        winston.format.splat(),
		winston.format.printf(({ timestamp, level, message, filename }) => {
			//const fileInfo = file ? ` [${file}]` : '';
			return `[${timestamp}] [${level.toUpperCase()}] [${filename}] ${message}`;
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