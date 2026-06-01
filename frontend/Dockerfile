FROM node:20-alpine

WORKDIR /app

COPY package.json ./
# Assuming package-lock.json is copied as well if it exists, but will rely on npm install
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]