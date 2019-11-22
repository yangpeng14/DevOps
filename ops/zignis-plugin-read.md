## 什么是 zignis-plugin-read ？
这是一个简单的工具插件，目的是实现一个能够方便的`获取网页主体`的`命令行工具`，以方便我们以各种方式`搜集整理学习资料`，`支持各种格式`，有一些特色模式，为了简单这里也称之为格式。

## 支持的格式
格式名称 | 解释
---|---
markdown , md | 一种纯文本格式的标记语言
pdf | 便携式文件格式
html | 生成一个html页面文件
png | 无损压缩的位图图形格式
jpeg | 有损压缩图片格式
less | 高亮阅读
web | 把 markdown 输出成网页，并集成了 Markdown 编辑器，即可以查看，也可以修改
epub | 电子书格式
mobi | 亚马逊电子书格式
console | 将 markdown 直接输出到终端，可以按需处理

## 主要参数
选项 | 解释
---|---
--version | 显示版本号
--format, -F | 需要转换的格式
--read-only, --ro | 只呈现html，与web格式一起使用
--debug | 调试
--port | 代理，比如抓取掘金文章中图片就需要开启
--localhost | 本地主机端口
--open-browser, --ob | Web格式自动打开浏览器
--rename | 获取的文章重新命名
--dir | 获取的文章存储本地位置

## 安装
```bash
$ npm i -g zignis zignis-plugin-read

# 默认会下载 puppeteer，比较慢，加上这个环境变量就不下了，也可以 `Ctrl+C` 取消下载
# 没有 puppeterr， `html`, `png`, `jpeg` 和 `pdf` 就不能工作了。
$ PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true npm i -g zignis zignis-plugin-read

# 用法
$ zignis read [URL|本地 markdown] --format=[FORMAT]

# 帮助
$ zignis read [url]
```

## 例子
```bash
# 获取掘金一篇文章
$ zignis read https://juejin.im/post/5dd6a8106fb9a05a7f75fe74 

# 获取掘金一篇文章，转换为 markdown 格式
$ zignis read https://juejin.im/post/5dd6a8106fb9a05a7f75fe74 --format=markdown

# 打开一个空的 markdown 编辑器
$ zignis read --format=web 

# 欣赏一下自己项目的 README
$ zignis read README.md
```

## 获取文章转换成微信公众号支持的格式
```bash
# 安装
$ npm i -g zignis zignis-plugin-read zignis-plugin-read-extend-format-wechat

# 例子，抓取掘金文章，并使用代理获取文章中图片
$ zignis read https://juejin.im/post/5dd6a8106fb9a05a7f75fe74 --format=wechat --proxy
```

## 目前适合网页主体转换的网站
开发过程中发现，默认行为总是不尽如人意，需要针对性的调优，目前只对下列网站做过基本调优，不保证绝对没有问题，遇到一个解决一个。

- 掘金
- 简书
- 知乎

## 已知 BUG
- 生成 `mobi` 格式时，`远程图片会丢失`，可以先转成 `epub`，然后自己用 ebook-convert 转成 mobi

## 项目地址
- `zignis-plugin-read` https://github.com/vipzhicheng/zignis-plugin-read
- `zignis-plugin-read-extend-format-wechat` https://github.com/vipzhicheng/zignis-plugin-read-extend-format-wechat

## 使用过程中程序 Bug 反馈
- 可以直接在公众号留言，我会`第一时间`反馈给`作者`
- 可以到上面`Github`项目中提交`Issues`


## 结束语
如果这个`神器`给你带来便利，花费你几秒宝贵的时间到`Github`点击一个`Star`
