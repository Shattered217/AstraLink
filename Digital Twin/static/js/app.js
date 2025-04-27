// 获取DOM元素
const statusText = document.getElementById("status");
const statusDot = document.getElementById("status-dot");
const wifiText = document.getElementById("wifi-text");
const wifiBars = [
  document.getElementById("wifi-bar-1"),
  document.getElementById("wifi-bar-2"),
  document.getElementById("wifi-bar-3"),
  document.getElementById("wifi-bar-4"),
  document.getElementById("wifi-bar-5"),
];
const chatContainer = document.getElementById("chat-container");
// 初始化轮询函数
function initPolling() {
  // WiFi质量轮询
  function pollWifi() {
    fetch("/api/wifi")
      .then((response) => response.json())
      .then((data) => {
        wifiText.textContent = data.wifi_quality;
        updateWifiBars(data.wifi_quality);
      })
      .catch(/* 错误处理 */);
  }

  // 历史对话轮询
  function pollHistory() {
    fetch("/api/history")
      .then((response) => response.json())
      .then((data) => {
        renderChatMessages(data.history);
      })
      .catch(/* 错误处理 */);
  }

  // 设置轮询间隔
  setInterval(pollWifi, 3000);
  setInterval(pollHistory, 3000);

  // 立即执行首次请求
  pollWifi();
  pollHistory();
}

// 初始化应用
document.addEventListener("DOMContentLoaded", () => {
  initPolling();
  // 获取状态并更新显示=
  function updateStatusDisplay() {
    fetch("/api/status")
      .then((response) => response.json())
      .then((data) => {
        const statusElement = document.getElementById("status");
        const statusDot = document.getElementById("status-dot");

        if (data.status === 1) {
          statusElement.textContent = "运行中"; // 状态为 1 时，显示“运行中”
          statusDot.style.backgroundColor = "green"; // 更改状态点为绿色
        } else if (data.status === 0) {
          statusElement.textContent = "待机"; // 状态为 0 时，显示“待机”
          statusDot.style.backgroundColor = "gray"; // 更改状态点为红色
        } else {
          statusElement.textContent = "未知状态"; // 如果状态值不是 0 或 1，显示“未知状态”
          statusDot.style.backgroundColor = "red"; // 设置为灰色
        }
      })
      .catch((error) => {
        console.error("获取状态时发生错误:", error);
        const statusElement = document.getElementById("status");
        const statusDot = document.getElementById("status-dot");
        statusElement.textContent = "无法获取状态"; // 请求失败时显示错误消息
        statusDot.style.backgroundColor = "gray"; // 设置为灰色
      });
  }
  setInterval(updateStatusDisplay, 2000);
  window.onload = updateStatusDisplay;

  // 获取WiFi质量
  fetch("/api/wifi")
    .then((response) => response.json())
    .then((data) => {
      wifiText.textContent = data.wifi_quality;
      updateWifiBars(data.wifi_quality);
    })
    .catch((error) => {
      console.error("获取WiFi质量失败:", error);
      wifiText.textContent = "获取失败";
    });

  // 获取历史对话
  fetch("/api/history")
    .then((response) => response.json())
    .then((data) => {
      renderChatMessages(data.history);
    })
    .catch((error) => {
      console.error("获取历史对话失败:", error);
      chatContainer.innerHTML =
        '<div class="error-message">加载历史对话失败</div>';
    });
});

// 更新WiFi信号条
function updateWifiBars(quality) {
  // 重置所有条
  wifiBars.forEach((bar) => bar.classList.remove("active"));

  // 处理未连接情况
  if (typeof quality === "string" && quality.includes("未连接")) {
    return;
  }

  let qualityValue = 0;

  if (typeof quality === "number") {
    qualityValue = quality;
  } else if (typeof quality === "string") {
    const match = quality.match(/\d+/);
    qualityValue = match ? parseInt(match[0]) : 0;
  }

  // 限制在 0-100 范围内
  qualityValue = Math.max(0, Math.min(qualityValue, 100));

  const activeBars = Math.ceil(qualityValue / 20);

  for (let i = 0; i < activeBars; i++) {
    wifiBars[i].classList.add("active");
  }
}

// 渲染聊天消息
function renderChatMessages(messages) {
  chatContainer.innerHTML = "";

  if (messages.length === 0) {
    chatContainer.innerHTML = '<div class="info-message">暂无历史对话</div>';
    return;
  }

  messages.forEach((message) => {
    const questionElement = document.createElement("div");
    questionElement.className = "chat-message message-sent";

    const questionContentElement = document.createElement("div");
    questionContentElement.className = "message-content";
    questionContentElement.textContent = message.message; // 显示问题

    const questionTimeElement = document.createElement("div");
    questionTimeElement.className = "message-time";
    const questionFormattedTime = message.timestamp.split(".")[0]; // 去掉微秒部分
    questionTimeElement.textContent = questionFormattedTime || "未知时间";

    questionElement.appendChild(questionContentElement);
    questionElement.appendChild(questionTimeElement);
    chatContainer.appendChild(questionElement);

    // 系统回复的消息（回答）
    const answerElement = document.createElement("div");
    answerElement.className = "chat-message message-received";

    const answerContentElement = document.createElement("div");
    answerContentElement.className = "message-content";
    answerContentElement.textContent = message.response; // 显示回答

    const answerTimeElement = document.createElement("div");
    answerTimeElement.className = "message-time";
    answerTimeElement.textContent = questionFormattedTime || "未知时间"; // 使用相同的时间戳

    answerElement.appendChild(answerContentElement);
    answerElement.appendChild(answerTimeElement);
    chatContainer.appendChild(answerElement);
  });

  // 滚动到底部
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
