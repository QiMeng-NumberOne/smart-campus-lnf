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
      // 调用微信登录API
      wx.login({
        success: (res) => {
          if (res.code) {
            // 这里可以将code发送到后端进行登录
            console.log('微信登录code:', res.code);
            this.setData({
              showPrivacyModal: true
            });
          } else {
            wx.showToast({
              title: '登录失败，请重试',
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          wx.showToast({
            title: '登录失败，请重试',
            icon: 'none'
          });
          console.error('微信登录失败:', err);
        },
        complete: () => {
          wx.hideLoading();
        }
      });
    } catch (error) {
      wx.hideLoading();
      wx.showToast({
        title: '登录失败，请重试',
        icon: 'none'
      });
      console.error('登录错误:', error);
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