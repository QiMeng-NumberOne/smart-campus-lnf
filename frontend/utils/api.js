const { request, getActiveBaseUrl } = require("./request");

function sanitizeFormData(data) {
  if (!data || typeof data !== "object") return {};
  const next = {};
  Object.keys(data).forEach((key) => {
    const value = data[key];
    if (value !== undefined && value !== null && value !== "") {
      next[key] = value;
    }
  });
  return next;
}

function uploadFile(filePath) {
  const baseUrl = getActiveBaseUrl();
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}/api/v1/common/upload`,
      filePath,
      name: "file",
      success: (res) => {
        try {
          const data = JSON.parse(res.data || "{}");
          resolve(data);
        } catch (error) {
          reject(error);
        }
      },
      fail: reject
    });
  });
}

function searchByImage(filePath, formData = {}) {
  const baseUrl = getActiveBaseUrl();
  const safeFormData = sanitizeFormData(formData);
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}/api/v1/search/by-image`,
      filePath,
      name: "file",
      formData: safeFormData,
      success: (res) => {
        try {
          const data = JSON.parse(res.data || "{}");
          resolve(data);
        } catch (error) {
          reject(error);
        }
      },
      fail: reject
    });
  });
}

function searchByText(params = {}) {
  return request({ url: "/api/v1/search/by-text", method: "GET", data: params });
}

function listItems(params = {}) {
  return request({ url: "/api/v1/items", method: "GET", data: params });
}

function createItem(payload) {
  return request({ url: "/api/v1/items", method: "POST", data: payload });
}

function updateItemStatus(itemId, payload) {
  return request({ url: `/api/v1/items/${itemId}/status`, method: "PUT", data: payload });
}

function recognizeItemImage(itemId, payload = {}) {
  return request({ url: `/api/v1/ai/recognize/item/${itemId}`, method: "POST", data: payload });
}

function recognizeImageUrl(payload = {}) {
  return request({ url: "/api/v1/ai/recognize/image", method: "POST", data: payload });
}

function applyAiSuggestion(payload) {
  return request({ url: "/api/v1/ai/apply-suggestion", method: "POST", data: payload });
}

function ocrIdCard(payload = {}) {
  return request({ url: "/api/v1/ai/ocr/id-card", method: "POST", data: payload });
}

function getItemDetail(itemId) {
  return request({ url: `/api/v1/items/${itemId}`, method: "GET" });
}

function listComments(itemId, params = {}) {
  return request({ url: `/api/v1/items/${itemId}/comments`, method: "GET", data: params });
}

function createComment(itemId, payload) {
  return request({ url: `/api/v1/items/${itemId}/comments`, method: "POST", data: payload });
}

function myItems(params = {}) {
  return request({ url: "/api/v1/items/mine", method: "GET", data: params });
}

function addFavorite(itemId) {
  return request({ url: "/api/v1/favorites", method: "POST", data: { item_id: itemId } });
}

function removeFavorite(itemId) {
  return request({ url: `/api/v1/favorites/${itemId}`, method: "DELETE" });
}

function listFavorites() {
  return request({ url: "/api/v1/favorites", method: "GET" });
}

function listMessages(params = {}) {
  return request({ url: "/api/v1/messages", method: "GET", data: params });
}

function unreadCount() {
  return request({ url: "/api/v1/messages/unread-count", method: "GET" });
}

function markMessageRead(messageId) {
  return request({ url: `/api/v1/messages/${messageId}/read`, method: "POST" });
}

function me() {
  return request({ url: "/api/v1/auth/me", method: "GET" });
}

function updateProfile(payload) {
  return request({ url: "/api/v1/auth/me", method: "PUT", data: payload });
}

function login(payload) {
  return request({ url: "/api/v1/auth/login", method: "POST", data: payload });
}

function register(payload) {
  return request({ url: "/api/v1/auth/register", method: "POST", data: payload });
}

module.exports = {
  uploadFile,
  searchByImage,
  searchByText,
  listItems,
  createItem,
  updateItemStatus,
  recognizeItemImage,
  recognizeImageUrl,
  applyAiSuggestion,
  ocrIdCard,
  getItemDetail,
  listComments,
  createComment,
  myItems,
  addFavorite,
  removeFavorite,
  listFavorites,
  listMessages,
  unreadCount,
  markMessageRead,
  me,
  updateProfile,
  login,
  register
};
