// 发布页面逻辑
Page({
  data: {
    publishType: 'lost', // lost 寻物, found 招领
    selectedContactMethod: 'wechat',
    formData: {
      title: '',
      description: '',
      category: '',
      lostTime: '2024-03-26 14:30',
      location: '',
      contactInfo: ''
    },
    images: []
  },

  // 页面加载
  onLoad(options) {
    console.log('发布页面加载');
  },

  // 返回
  goBack() {
    wx.navigateBack();
  },

  // 切换发布类型
  togglePublishType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      publishType: type === 'lost' ? 'found' : 'lost'
    });
    this.updatePageTitle();
  },

  // 更新页面标题
  updatePageTitle() {
    const title = this.data.publishType === 'lost' ? '发布失物招领' : '发布寻物启事';
    const btnText = this.data.publishType === 'lost' ? '寻物' : '失物';
    this.setData({
      'formData.title': '',
      'formData.description': '',
      'formData.location': ''
    });
  },

  // 选择图片
  chooseImage() {
    wx.chooseImage({
      count: 6 - this.data.images.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const newImages = this.data.images.concat(res.tempFilePaths);
        this.setData({
          images: newImages
        });
        console.log('选择的图片:', newImages);
      }
    });
  },

  // 选择分类
  chooseCategory() {
    const categories = ['电子设备', '证件', '服装', '其他'];
    wx.showActionSheet({
      itemList: categories,
      success: (res) => {
        const category = categories[res.tapIndex];
        this.setData({
          'formData.category': category
        });
      }
    });
  },

  // 选择时间
  chooseTime() {
    wx.showPickerModal({
      type: 'datetime',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            'formData.lostTime': res.dateString
          });
        }
      }
    });
  },

  // 选择地点
  chooseLocation() {
    const locations = ['图书馆', '教学楼', '宿舍楼', '食堂', '操场', '其他'];
    wx.showActionSheet({
      itemList: locations,
      success: (res) => {
        const location = locations[res.tapIndex];
        this.setData({
          'formData.location': location
        });
      }
    });
  },

  // 选择联系方式
  selectContactMethod(e) {
    const method = e.currentTarget.dataset.method;
    this.setData({
      selectedContactMethod: method
    });
  },

  // 标题输入
  onTitleChange(e) {
    this.setData({
      'formData.title': e.detail.value
    });
  },

  // 描述输入
  onDescriptionChange(e) {
    this.setData({
      'formData.description': e.detail.value
    });
  },

  // 联系方式输入
  onContactChange(e) {
    this.setData({
      'formData.contactInfo': e.detail.value
    });
  },

  // 提交发布
  submitPublish() {
    const { title, description, category, location, contactInfo } = this.data.formData;
    
    // 验证
    if (!title) {
      wx.showToast({ title: '请输入物品名称', icon: 'none' });
      return;
    }
    if (!description) {
      wx.showToast({ title: '请输入详细描述', icon: 'none' });
      return;
    }
    if (!category) {
      wx.showToast({ title: '请选择物品分类', icon: 'none' });
      return;
    }
    if (!location) {
      wx.showToast({ title: '请选择地点', icon: 'none' });
      return;
    }
    if (!contactInfo) {
      wx.showToast({ title: '请输入联系方式', icon: 'none' });
      return;
    }

    wx.showLoading({
      title: '发布中...'
    });

    // 模拟发布
    setTimeout(() => {
      wx.hideLoading();
      wx.showToast({
        title: '发布成功！',
        icon: 'success'
      });
      wx.switchTab({
        url: '/pages/home/home'
      });
    }, 1000);
  }
});