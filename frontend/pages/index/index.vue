<template>
  <view class="container">
    <view class="header">
      <input class="search-input" type="text" placeholder="搜索你丢失的物品，如：水杯、校园卡..." />
    </view>

    <view class="tabs">
      <view class="tab active">寻物启事 (Lost)</view>
      <view class="tab">失物招领 (Found)</view>
    </view>

    <view class="list">
      <view class="card" v-for="(item, index) in items" :key="index">
        <view class="card-content">
          <view class="title">{{ item.name }}</view>
          <view class="desc">地点：{{ item.location }}</view>
          <view class="time">时间：{{ item.time }}</view>
        </view>
        <view class="status" :class="item.type === 'lost' ? 'status-lost' : 'status-found'">
          {{ item.type === 'lost' ? '急寻' : '待认领' }}
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';

// 模拟的后台数据
const items = ref([
  { name: '一串带有皮卡丘挂件的钥匙', location: '第一教学楼 302 教室', time: '今天上午 10:00', type: 'lost' },
  { name: '蓝色 AirPods 耳机盒', location: '图书馆二楼阅览室', time: '昨天下午 15:30', type: 'found' },
  { name: '李雷的校园一卡通', location: '南区第三食堂', time: '昨天中午 12:00', type: 'lost' }
]);
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20rpx;
}

.header {
  margin-bottom: 30rpx;
}

.search-input {
  background-color: #ffffff;
  padding: 20rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.05);
}

.tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30rpx;
  background-color: #ffffff;
  padding: 20rpx 0;
  border-radius: 20rpx;
}

.tab {
  font-size: 32rpx;
  color: #666;
}

.tab.active {
  color: #007aff;
  font-weight: bold;
  border-bottom: 4rpx solid #007aff;
}

.card {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}

.card-content .title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.card-content .desc, .card-content .time {
  font-size: 26rpx;
  color: #888;
  margin-top: 6rpx;
}

.status {
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
  font-weight: bold;
}

.status-lost {
  background-color: #ffeef0;
  color: #ff4d4f;
}

.status-found {
  background-color: #e6f7ff;
  color: #1890ff;
}
</style>