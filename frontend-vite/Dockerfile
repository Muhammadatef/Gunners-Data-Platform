FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Expose port
EXPOSE 3000

# Use development mode with hot reload for better debugging
# Change to "npm run build && npm run preview" for production
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
