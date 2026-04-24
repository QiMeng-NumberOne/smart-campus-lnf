function sanitizeData(data) {
  if (!data || typeof data !== "object") return data;
  const next = {};
  Object.keys(data).forEach((key) => {
    const value = data[key];
    if (value !== undefined) {
      next[key] = value;
    }
  });
  return next;
}

function request({ url, method = "GET", data, header = {} }) {
  const app = getApp();
  const baseUrls = app?.globalData?.baseUrls?.length
    ? app.globalData.baseUrls
    : [app?.globalData?.baseUrl || ""];
  const token = wx.getStorageSync("token");

  return new Promise((resolve, reject) => {
    let idx = 0;
    const tryRequest = () => {
      const baseUrl = baseUrls[idx];
      const payload = sanitizeData(data);
      wx.request({
        url: `${baseUrl}${url}`,
        method,
        data: payload,
        header: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...header
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            // 记录当前可用地址
            if (app?.globalData) app.globalData.baseUrl = baseUrl;
            resolve(res.data);
            return;
          }
          const detail = res?.data?.detail || res?.data?.message || "";
          reject(new Error(detail ? `HTTP ${res.statusCode}: ${detail}` : `HTTP ${res.statusCode}`));
        },
        fail: (err) => {
          idx += 1;
          if (idx < baseUrls.length) {
            tryRequest();
            return;
          }
          reject(err);
        }
      });
    };
    tryRequest();
  });
}

function getActiveBaseUrl() {
  const app = getApp();
  return app?.globalData?.baseUrl || "";
}

module.exports = {
  request,
  getActiveBaseUrl
};
