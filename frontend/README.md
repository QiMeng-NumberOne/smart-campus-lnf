# 校园失物招领小程序

这是一个基于微信小程序开发的校园失物招领平台，包含完整的前端代码结构。

## 项目结构

```
shiwuzhaoling/
├── app.json              # 小程序配置文件
├── sitemap.json          # 小程序搜索配置
├── pages/
│   ├── login/            # 登录页面
│   │   ├── login.wxml
│   │   ├── login.wxss
│   │   └── login.js
│   ├── home/             # 首页
│   │   ├── home.wxml
│   │   ├── home.wxss
│   │   └── home.js
│   ├── publish/          # 发布页面
│   │   ├── publish.wxml
│   │   ├── publish.wxss
│   │   └── publish.js
│   ├── message/          # 消息页面
│   │   ├── message.wxml
│   │   ├── message.wxss
│   │   ├── message.js
│   │   ├── system/       # 系统通知
│   │   ├── match/        # 匹配通知
│   │   ├── reply/        # 回复通知
│   │   └── settings/     # 消息设置
│   └── profile/          # 个人中心
│       ├── profile.wxml
│       ├── profile.wxss
│       └── profile.js
└── images/               # 图片资源（需自行创建）
```

## 功能说明

1. **登录页面**：微信一键登录、游客模式
2. **首页**：失物/招领切换、分类筛选、搜索功能
3. **发布页面**：发布寻物启事和失物招领
4. **消息页面**：系统通知、匹配通知、回复通知、消息设置
5. **个人中心**：用户信息、发布记录、信用等级

## 如何使用

1. 在微信开发者工具中打开项目
2. 选择"导入项目"
3. 填写项目名称和项目路径
4. 选择小程序AppID（可以使用测试号）
5. 点击"导入"
6. 编译并预览

## 开发说明

- 所有页面都使用了微信小程序的标准语法
- 页面跳转使用 `wx.navigateTo`、`wx.switchTab` 等API
- 数据存储使用 `wx.setStorageSync`、`wx.getStorageSync`
- 图片选择使用 `wx.chooseImage`
- 网络请求使用模拟数据，实际使用时需要替换为真实API

## 注意事项

- 需要在 `images` 目录中添加相应的图标文件
- 实际部署时需要配置真实的后端API地址
- 微信登录功能需要在小程序后台配置相应的权限

## 技术栈

- 微信小程序原生框架
- WXML + WXSS + JavaScript
- 微信小程序API