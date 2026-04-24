const { login, register } = require("../../utils/api");

// 登录页面逻辑
Page({
  data: {
    agreementChecked: true,
    showPrivacyModal: false
  },

  // 同意协议变更
  onAgreementChange(e) {
    this.setData({
      agreementChecked: e.detail.value[0] ? true : false
    });
  },

  // 微信一键登录
  async handleWechatLogin() {
    if (!this.data.agreementChecked) {
      wx.showToast({
        title: '请先阅读并同意用户协议和隐私政策',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '登录中...'
    });

    try {
      // 开发工具模式优先走本地测试账号，不依赖 wx.login 权限
      try {
        await new Promise((resolve, reject) => {
          wx.login({
            success: resolve,
            fail: reject
          });
        });
      } catch (_) {}

      const account = "18800000000";
      const password = "123456";
      let data = null;
      try {
        const r = await login({ account, password });
        data = r?.data || null;
      } catch (_) {
        const r = await register({
          username: "微信用户",
          password,
          phone: account
        });
        data = r?.data || null;
      }
      if (!data?.token) {
        wx.showToast({
          title: '登录失败，请检查后端',
          icon: 'none'
        });
        return;
      }
      wx.setStorageSync("token", data.token);
      wx.setStorageSync("userInfo", data);
      this.setData({ showPrivacyModal: true });
    } catch (error) {
      wx.hideLoading();
      wx.showToast({
        title: '登录失败，请重编译后重试',
        icon: 'none'
      });
      console.error('登录错误:', error);
      return;
    }
    wx.hideLoading();
  },

  // 显示隐私提示弹窗
  showPrivacyModal() {
    this.setData({
      showPrivacyModal: true
    });
  },

  // 隐藏隐私提示弹窗
  hidePrivacyModal() {
    this.setData({
      showPrivacyModal: false
    });
  },

  // 跳转到首页
  goToHome() {
    this.setData({
      showPrivacyModal: false
    });
    wx.setStorageSync('isLoggedIn', true);
    wx.switchTab({
      url: '/pages/home/home'
    });
  },

  // 游客模式
  goToGuestMode() {
    wx.setStorageSync('isLoggedIn', false);
    wx.switchTab({
      url: '/pages/home/home'
    });
  },

  // 生命周期函数
  onLoad(options) {
    console.log('登录页面加载');
  },

  onShow() {
    console.log('登录页面显示');
  }
});