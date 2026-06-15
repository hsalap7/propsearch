FROM node:20-alpine
WORKDIR /app

# copy package manifest; package-lock.json may be absent during development
COPY package.json package-lock.json* ./

# If a lockfile exists use `npm ci` for reproducible installs, otherwise fall back to `npm install`.
# Use --omit=dev to avoid installing devDependencies in production image.
RUN if [ -f package-lock.json ]; then \
      npm ci --omit=dev --no-audit --no-fund; \
    else \
      npm install --omit=dev --no-audit --no-fund; \
    fi

COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
