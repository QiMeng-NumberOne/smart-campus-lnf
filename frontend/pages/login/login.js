const { wechatLogin, me, getLoginStats } = require("../../utils/api");

// 登录页面逻辑
Page({
  data: {
    agreementChecked: true,
    showPrivacyModal: false,
    stats: {
      resolvedCount: "--",
      userCount: "--",
      resolvedRate: "--"
    }
  },

  formatCount(n) {
    const value = Number(n || 0);
    return value.toLocaleString("zh-CN");
  },

  async loadLoginStats() {
    try {
      const res = await getLoginStats();
      const data = res?.data || {};
      this.setData({
        stats: {
          resolvedCount: this.formatCount(data.resolved_count),
          userCount: this.formatCount(data.user_count),
          resolvedRate: `${Number(data.resolved_rate || 0)}%`
        }
      });
    } catch (err) {
      console.warn("加载登录统计失败", err);
    }
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

    try {
      // 必须在用户点击事件调用栈里立即触发，否则会报：
      // getUserProfile:fail can only be invoked by user TAP gesture
      const profileRes = await new Promise((resolve, reject) => {
        wx.getUserProfile({
          desc: "用于完善您的头像和昵称",
          success: resolve,
          fail: reject
        });
      });
      const userInfo = profileRes?.userInfo || {};

      wx.showLoading({
        title: '登录中...'
      });

      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });
      if (!loginRes?.code) {
        wx.showToast({
          title: "未获取到微信登录凭证",
          icon: "none"
        });
        return;
      }

      const r = await wechatLogin({
        code: loginRes.code,
        nickname: userInfo.nickName || "",
        avatar: userInfo.avatarUrl || ""
      });
      const data = r?.data || null;
      if (!data?.token) {
        wx.showToast({
          title: '登录失败，请检查后端',
          icon: 'none'
        });
        return;
      }
      wx.setStorageSync("token", data.token);
      wx.setStorageSync("userInfo", data);
      wx.setStorageSync("isLoggedIn", true);
      this.setData({ showPrivacyModal: true });
    } catch (error) {
      wx.hideLoading();
      const msg = String(error?.errMsg || "");
      wx.showToast({
        title: msg.includes("getUserProfile:fail")
          ? "请点击并同意授权后登录"
          : '登录失败，请重编译后重试',
        icon: 'none'
      });
      console.error('登录错误:', error);
      return;
    }
    wx.hideLoading();
  },

  async autoSkipLoginIfValid() {
    const token = wx.getStorageSync("token");
    if (!token) return;
    try {
      await me();
      wx.setStorageSync("isLoggedIn", true);
      wx.switchTab({ url: "/pages/home/home" });
    } catch (_) {
      wx.removeStorageSync("token");
      wx.removeStorageSync("userInfo");
      wx.setStorageSync("isLoggedIn", false);
    }
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

  // 生命周期函数
  onLoad(options) {
    console.log('登录页面加载');
    this.loadLoginStats();
    this.autoSkipLoginIfValid();
  },

  onShow() {
    console.log('登录页面显示');
    this.loadLoginStats();
    this.autoSkipLoginIfValid();
  }
});