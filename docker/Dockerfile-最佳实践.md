## Dockerfile 简介
Docker通过读取Dockerfile文件中的指令自动构建镜像。Dockerfile文件为一个文本文件，里面包含构建镜像所需的所有的命令。Dockerfile文件遵循特定的格式和指令集
Docker镜像由只读层组成，每个层都代表一个Dockerfile指令。这些层是堆叠的，每个层都是前一层变化的增量

## 遵守下面原则
- 使用小基础镜像(例：alpine)
- RUN指令中最好把所有shell命令都放在一起执行，减少`Docker层`
- `ADD` 或者 `COPY` 指令时一定要使用`--chown=node:node`（node:node 分别为用户组和附属组）并且`Dockerfile中一定要有node用户`，Dockerfile切换用户时不需要使用`chown`命令修改权限而导致镜像变大
- 分阶段构建
- 最好声明Docker镜像签名
- 使用`.dockerignore`排除不需要加入Docker镜像目录或者文件
- 不介意使用root用户

## 最佳实践
```
# stage 1
FROM node:13.1.0-alpine as builder

LABEL "name"="YP小站"
LABEL version="node 13.1.0"

# 修改alpine源为阿里源，安装tzdata包并修改为北京时间
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk --update add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 声明环境变量
ENV NODE_ENV development

# 声明使用node用户
USER node

# 首次只加入package.json文件，package.json一般不变，这样就可以充分利用Docker Cache，节约安装node包时间
COPY --chown=node:node package.json /app && npm ci

# 声明镜像默认位置
WORKDIR /app

# 加入node代码
ADD --chown=node:node . /app

# build代码
RUN npm run build \
    && mv dist public

# stage 2
# 加入nginx镜像
FROM nginx:alpine

# 拷贝上阶段build静态文件
COPY --from=builder /app/public /app/public

# 拷贝nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 声明容器端口
EXPOSE 8080

# 启动命令
CMD ["nginx","-g","daemon off;"]
```