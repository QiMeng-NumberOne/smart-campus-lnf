const { uploadFile, createItem, triggerItemMatchNotify, recognizeImageUrl, ocrIdCard } = require("../../utils/api");

// 发布页面逻辑
Page({
  data: {
    publishType: 'lost', // lost 寻物, found 招领
    pageTitle: "发布寻物启事",
    switchText: "切换为发布招领",
    submitText: "发布寻物启事",
    selectedContactMethod: 'wechat',
    formData: {
      title: '',
      description: '',
      category: '',
      itemTypeId: null,
      idCardName: "",
      idCardNo: "",
      studentNo: "",
      college: "",
      major: "",
      idCardAddress: "",
      lostDate: '2026-04-21',
      lostTime: '14:30',
      location: '',
      contactInfo: ''
    },
    images: [],
    uploadedImages: [],
    aiDetecting: false,
    aiSuggestion: null,
    aiAutoFillThreshold: 0.5,
    idCardOcrLoading: false,
    certInfoVisible: false,
    certDocType: "",
    certNoLabel: "证件号（仅加密存储，前台不展示）",
    certFieldVisible: {
      name: false,
      idNo: false,
      studentNo: false,
      college: false,
      major: false,
      address: false
    }
  },

  normalizeImageUrl(url = "") {
    if (!url) return "";
    return url
      .replace("http://127.0.0.1:8090", "http://127.0.0.1:8091")
      .replace("http://localhost:8090", "http://127.0.0.1:8091");
  },

  // 页面加载
  onLoad(options) {
    const type = options?.type;
    if (type === "found" || type === "lost") {
      this.setData({ publishType: type });
      this.updatePageTitle();
    }
  },

  // 返回
  goBack() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      wx.navigateBack();
      return;
    }
    wx.switchTab({
      url: "/pages/home/home"
    });
  },

  resetFormState() {
    const isLost = this.data.publishType === "lost";
    this.setData({
      pageTitle: isLost ? "发布寻物启事" : "发布失物招领",
      switchText: isLost ? "切换为发布招领" : "切换为发布寻物",
      submitText: isLost ? "发布寻物启事" : "发布失物招领",
      selectedContactMethod: "wechat",
      formData: {
        title: "",
        description: "",
        category: "",
        itemTypeId: null,
        idCardName: "",
        idCardNo: "",
        studentNo: "",
        college: "",
        major: "",
        idCardAddress: "",
        lostDate: "2026-04-21",
        lostTime: "14:30",
        location: "",
        contactInfo: ""
      },
      images: [],
      uploadedImages: [],
      aiSuggestion: null,
      aiDetecting: false,
      idCardOcrLoading: false,
      certInfoVisible: false,
      certDocType: "",
      certNoLabel: "证件号（仅加密存储，前台不展示）",
      certFieldVisible: {
        name: false,
        idNo: false,
        studentNo: false,
        college: false,
        major: false,
        address: false
      }
    });
  },

  // 切换发布类型
  togglePublishType() {
    this.setData({
      publishType: this.data.publishType === 'lost' ? 'found' : 'lost'
    });
    this.updatePageTitle();
  },

  // 更新页面标题
  updatePageTitle() {
    const isLost = this.data.publishType === "lost";
    const pageTitle = isLost ? "发布寻物启事" : "发布失物招领";
    const switchText = isLost ? "切换为发布招领" : "切换为发布寻物";
    const submitText = isLost ? "发布寻物启事" : "发布失物招领";
    this.setData({
      pageTitle,
      switchText,
      submitText,
      'formData.title': '',
      'formData.description': '',
      'formData.location': '',
      'formData.itemTypeId': null,
      'formData.idCardName': '',
      'formData.idCardNo': '',
      'formData.studentNo': '',
      'formData.college': '',
      'formData.major': '',
      'formData.idCardAddress': '',
      aiSuggestion: null,
      certInfoVisible: false,
      certDocType: "",
      certNoLabel: "证件号（仅加密存储，前台不展示）",
      certFieldVisible: {
        name: false,
        idNo: false,
        studentNo: false,
        college: false,
        major: false,
        address: false
      }
    });
  },

  resetCertFormFields() {
    this.setData({
      certInfoVisible: false,
      certDocType: "",
      certNoLabel: "证件号（仅加密存储，前台不展示）",
      certFieldVisible: {
        name: false,
        idNo: false,
        studentNo: false,
        college: false,
        major: false,
        address: false
      },
      "formData.idCardName": "",
      "formData.idCardNo": "",
      "formData.studentNo": "",
      "formData.college": "",
      "formData.major": "",
      "formData.idCardAddress": ""
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
        const newUploaded = this.data.uploadedImages.concat(res.tempFilePaths.map(() => null));
        this.setData({
          images: newImages,
          uploadedImages: newUploaded
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
        const typeIdMap = { "电子设备": 4, "证件": 9, "服装": 7, "其他": 10 };
        this.setData({
          'formData.category': category,
          'formData.itemTypeId': typeIdMap[category] || null
        });
        if (category === "证件") {
          wx.showModal({
            title: "证件隐私强提醒",
            content: "请先点击 OCR 识别，系统会自动显示可填写字段；识别有误可手动补录。",
            confirmText: "去识别",
            cancelText: "稍后",
            success: (modalRes) => {
              if (modalRes.confirm) {
                this.autoFillIdCardByOcr();
              }
            }
          });
        } else {
          this.resetCertFormFields();
        }
      }
    });
  },

  mapAiTypeToCategory(typeName = "") {
    const text = (typeName || "").toLowerCase();
    if (["id_card", "campus_card", "card", "证件", "身份证", "校园卡"].some((k) => text.includes(k))) {
      return "证件";
    }
    if (["bag", "书包", "衣", "服装"].some((k) => text.includes(k))) {
      return "服装";
    }
    if (["phone", "earphone", "电子", "keys", "glasses", "wallet", "cup", "umbrella"].some((k) => text.includes(k))) {
      return "电子设备";
    }
    return "其他";
  },

  detectCategoryByAi() {
    if (this.data.aiDetecting) return;
    if (!this.data.images.length) {
      wx.showToast({ title: "请先上传图片", icon: "none" });
      return;
    }
    const firstPath = this.data.images[0];
    const cached = this.data.uploadedImages[0];
    this.setData({ aiDetecting: true });

    const ensureUploaded = cached
      ? Promise.resolve({ data: { url: cached } })
      : uploadFile(firstPath).then((res) => {
          const url = res?.data?.url || "";
          const next = [...this.data.uploadedImages];
          next[0] = url;
          this.setData({ uploadedImages: next });
          return res;
        });

    ensureUploaded
      .then((uploadRes) => {
        const imageUrl = this.normalizeImageUrl(uploadRes?.data?.url);
        if (!imageUrl) throw new Error("图片上传失败");
        return recognizeImageUrl({ image_url: imageUrl });
      })
      .then((res) => {
        const suggest = res?.data || {};
        const displayName = suggest.item_type_name || suggest.item_class || "未知";
        const confidence = Number(suggest.confidence || 0);
        const shouldAutoFill = confidence >= this.data.aiAutoFillThreshold;
        const patch = { aiSuggestion: suggest };
        if (shouldAutoFill) {
          const category = this.mapAiTypeToCategory(displayName);
          patch["formData.category"] = category;
          patch["formData.itemTypeId"] = suggest.item_type_id || null;
          if (!this.data.formData.title && displayName && displayName !== "unknown") {
            patch["formData.title"] = displayName;
          }
          wx.showToast({ title: "识别可信，已自动填充", icon: "none" });
        } else {
          wx.showToast({ title: "置信度较低，仅展示建议", icon: "none" });
        }
        this.setData(patch);
        wx.showToast({
          title: "识别结果仅供参考，如有误请手动修改",
          icon: "none",
          duration: 2200
        });
        if ((suggest.item_class || "").toLowerCase() === "id_card" || Number(suggest.item_type_id) === 9) {
          wx.showModal({
            title: "证件隐私强提醒",
            content: "检测到可能是身份证/校园卡。请优先遮挡证号、地址、人像，仅保留姓名可见。",
            showCancel: false
          });
          this.autoFillIdCardByOcr();
        }
      })
      .catch((err) => {
        wx.showToast({ title: err?.message?.slice(0, 22) || "AI识别失败", icon: "none" });
      })
      .finally(() => {
        this.setData({ aiDetecting: false });
      });
  },

  onDateChange(e) {
    this.setData({
      "formData.lostDate": e.detail.value
    });
  },

  onTimeChange(e) {
    this.setData({
      "formData.lostTime": e.detail.value
    });
  },

  // 删除图片
  removeImage(e) {
    const index = e.currentTarget.dataset.index;
    const images = [...this.data.images];
    const uploadedImages = [...this.data.uploadedImages];
    images.splice(index, 1);
    uploadedImages.splice(index, 1);
    const patch = {
      images,
      uploadedImages
    };
    // 删除首图后，清空基于首图得到的 AI 建议，避免用旧结果发布
    if (index === 0) {
      patch.aiSuggestion = null;
      patch["formData.itemTypeId"] = null;
      patch.certInfoVisible = false;
      patch.certDocType = "";
      patch.certFieldVisible = { name: false, idNo: false, studentNo: false, college: false, major: false, address: false };
    }
    this.setData(patch);
  },

  showCertFieldsByData(data = {}, manual = false) {
    const present = Array.isArray(data.present_fields) ? data.present_fields : [];
    const docType = data.doc_type || "";
    const isCampus = docType === "campus_card";
    const fieldVisible = manual
      ? { name: true, idNo: !isCampus, studentNo: isCampus, college: isCampus, major: isCampus, address: true }
      : {
          name: present.includes("name"),
          idNo: present.includes("id_no"),
          studentNo: present.includes("student_no"),
          college: present.includes("college"),
          major: present.includes("major"),
          address: present.includes("address")
        };
    this.setData({
      certInfoVisible: true,
      certDocType: docType,
      certNoLabel: isCampus ? "学号（仅加密存储，前台不展示）" : "身份证号（仅加密存储，前台不展示）",
      certFieldVisible: fieldVisible
    });
  },

  showManualCertFields() {
    const isCampus = this.data.certDocType === "campus_card";
    this.showCertFieldsByData({ doc_type: isCampus ? "campus_card" : "id_card" }, true);
  },

  previewImage(e) {
    const index = Number(e.currentTarget.dataset.index || 0);
    const urls = this.data.images || [];
    if (!urls.length) return;
    wx.previewImage({
      current: urls[index] || urls[0],
      urls
    });
  },

  autoFillIdCardByOcr() {
    if (this.data.idCardOcrLoading) return;
    if (!this.data.images.length) {
      wx.showToast({ title: "请先上传证件图片", icon: "none" });
      return;
    }
    const firstPath = this.data.images[0];
    const cached = this.data.uploadedImages[0];
    this.setData({ idCardOcrLoading: true });
    const ensureUploaded = cached
      ? Promise.resolve({ data: { url: cached } })
      : uploadFile(firstPath).then((res) => {
          const url = res?.data?.url || "";
          const next = [...this.data.uploadedImages];
          next[0] = url;
          this.setData({ uploadedImages: next });
          return res;
        });
    ensureUploaded
      .then((uploadRes) => {
        const imageUrl = this.normalizeImageUrl(uploadRes?.data?.url);
        if (!imageUrl) throw new Error("图片上传失败");
        return ocrIdCard({ image_url: imageUrl });
      })
      .then((res) => {
        const data = res?.data || {};
        const hasResult = !!(data.name || data.id_no || data.student_no || data.address);
        this.showCertFieldsByData(data, false);
        this.setData({
          "formData.idCardName": data.name || this.data.formData.idCardName,
          "formData.idCardNo": data.id_no || this.data.formData.idCardNo,
          "formData.studentNo": data.student_no || this.data.formData.studentNo,
          "formData.college": data.college || this.data.formData.college,
          "formData.major": data.major || this.data.formData.major,
          "formData.idCardAddress": data.address || this.data.formData.idCardAddress
        });
        if (hasResult) {
          wx.showToast({ title: "OCR识别成功，已自动填充", icon: "none" });
        } else {
          wx.showToast({
            title: data.ocr_error ? "OCR无有效结果，请换证件正面图重试" : "未识别到姓名/证件号/地址",
            icon: "none"
          });
        }
      })
      .catch(() => {
        wx.showToast({ title: "OCR暂不可用，请手动填写", icon: "none" });
        this.showManualCertFields();
      })
      .finally(() => this.setData({ idCardOcrLoading: false }));
  },

  // 选择地点
  chooseLocation() {
    const title = this.data.publishType === "lost" ? "选择丢失地点" : "选择拾到地点";
    wx.navigateTo({
      url: "/pages/location-picker/location-picker",
      success: (res) => {
        res.eventChannel.emit("initData", {
          selected: this.data.formData.location || "",
          pageTitle: title,
        });
        res.eventChannel.on("locationSelected", ({ location }) => {
          this.setData({ "formData.location": location || "" });
        });
      },
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

  onIdCardNameChange(e) {
    this.setData({ "formData.idCardName": e.detail.value || "" });
  },

  onIdCardNoChange(e) {
    this.setData({ "formData.idCardNo": e.detail.value || "" });
  },

  onIdCardAddressChange(e) {
    this.setData({ "formData.idCardAddress": e.detail.value || "" });
  },

  onStudentNoChange(e) {
    this.setData({ "formData.studentNo": e.detail.value || "" });
  },

  onCollegeChange(e) {
    this.setData({ "formData.college": e.detail.value || "" });
  },

  onMajorChange(e) {
    this.setData({ "formData.major": e.detail.value || "" });
  },

  clearForm() {
    wx.showModal({
      title: "清空内容",
      content: "确定清空当前已填写的全部内容吗？",
      confirmText: "清空",
      confirmColor: "#ef4444",
      success: (res) => {
        if (!res.confirm) return;
        this.resetFormState();
        wx.pageScrollTo({ scrollTop: 0, duration: 200 });
        wx.showToast({ title: "已清空", icon: "none" });
      }
    });
  },

  // 提交发布
  submitPublish() {
    const token = wx.getStorageSync("token");
    if (!token) {
      wx.showToast({ title: "请先登录后发布", icon: "none" });
      return;
    }
    const { title, description, category, location, contactInfo, lostDate, lostTime, itemTypeId, idCardName, idCardNo, studentNo, college, major, idCardAddress } = this.data.formData;
    const isCertCategory = category === "证件" || Number(itemTypeId) === 9;
    
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
    if (isCertCategory && !idCardName.trim()) {
      wx.showToast({ title: "证件类请填写姓名", icon: "none" });
      return;
    }

    wx.showLoading({
      title: '发布中...'
    });

    Promise.all(this.data.images.map((path) => uploadFile(path)))
      .then((uploadResults) => {
        const images = uploadResults
          .map((res) => res?.data?.url)
          .filter(Boolean)
          .map((url) => ({ url }));

        const payload = {
          item_type: this.data.publishType === "lost" ? 1 : 2,
          item_type_id: isCertCategory ? 9 : (itemTypeId || null),
          title,
          description,
          location_detail: location,
          lost_found_time: `${lostDate} ${lostTime}:00`,
          contact_info: contactInfo,
          images,
          id_card_info: isCertCategory ? {
            name: idCardName || "",
            id_no: idCardNo || "",
            student_no: studentNo || "",
            college: college || "",
            major: major || "",
            address: idCardAddress || "",
            doc_type: this.data.certDocType || "id_card",
            source: "manual"
          } : null
        };
        return createItem(payload);
      })
      .then((res) => {
        wx.hideLoading();
        const createdItemId = Number(res?.data?.id || 0);
        const initialCount = Number(res?.data?.match_notify_count || 0);
        const fallback = createdItemId
          ? triggerItemMatchNotify(createdItemId).then((r) => Number(r?.data?.match_notify_count || 0)).catch(() => 0)
          : Promise.resolve(0);
        return fallback.then((fallbackCount) => {
          this.resetFormState();
          const notifyCount = Math.max(initialCount, fallbackCount);
        const baseTitle = this.data.publishType === "lost" ? "寻物发布成功" : "招领发布成功";
        wx.showToast({
          title: notifyCount > 0 ? `${baseTitle}，已匹配${notifyCount}条` : baseTitle,
          icon: 'success'
        });
        wx.switchTab({
          url: '/pages/home/home'
        });
        });
      })
      .catch((err) => {
        wx.hideLoading();
        console.error("发布失败:", err);
        wx.showToast({
          title: err?.message?.slice(0, 20) || "发布失败",
          icon: "none"
        });
      });
  }
});