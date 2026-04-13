// 首页逻辑
Page({
  data: {
    currentTab: 'lost',
    currentCategory: '全部',
    items: []
  },

  // 页面加载
  onLoad(options) {
    console.log('首页加载');
    this.loadItemsList();
  },

  // 页面显示
  onShow() {
    console.log('首页显示');
  },

  // 加载物品列表
  loadItemsList() {
    wx.showLoading({
      title: '加载中...'
    });

    // 模拟数据
    const mockItems = [
      { id: 1, type: 'lost', category: '电子设备', title: '黑色双肩背包（含MacBook）', description: '黑色，带有校徽的双肩背包，内有一台MacBook Pro和充电器', location: '图书馆', date: '2024-03-25', user: '李同学', views: 156, commentCount: 3, status: 'active' },
      { id: 2, type: 'lost', category: '电子设备', title: 'AirPods Pro 无线耳机', description: '白色AirPods Pro，充电盒有轻微划痕', location: '教学楼', date: '2024-03-24', user: '张同学', views: 234, commentCount: 5, status: 'active' },
      { id: 3, type: 'lost', category: '其他', title: '蓝色折叠雨伞', description: '蓝色折叠雨伞，伞面有校园风景图案', location: '图书馆', date: '2024-03-23', user: '刘同学', views: 42, status: 'found' },
      { id: 4, type: 'lost', category: '其他', title: '红色帆布手提袋', description: '红色帆布手提袋，印有校园失物招领字样', location: '宿舍楼', date: '2024-03-22', user: '张同学', views: 78, status: 'active' }
    ];

    // 模拟API请求延迟
    setTimeout(() => {
      this.setData({
        items: mockItems
      });
      wx.hideLoading();
    }, 500);
  },

  // 切换标签
  switchTab(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      currentTab: type
    });
    this.loadItemsList();
  },

  // 切换分类
  switchCategory(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({
      currentCategory: category
    });
    this.loadItemsList();
  },

  // 搜索
  handleSearch(e) {
    const keyword = e.detail.value;
    console.log('搜索关键词:', keyword);
    // 这里可以调用搜索API
  },

  // 物品点击
  handleItemClick(e) {
    const itemId = e.currentTarget.dataset.id;
    console.log('点击物品:', itemId);
    // 这里可以跳转到物品详情页
    wx.showToast({
      title: '查看物品详情',
      icon: 'none'
    });
  },

  // 跳转到发布页面
  goToPublish() {
    wx.navigateTo({
      url: '/pages/publish/publish'
    });
  }
});