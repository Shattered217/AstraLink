function updateTime() {
  fetch("/api/time")
    .then((r) => r.json())
    .then((d) => {
      document.getElementById("time").innerText = d.time;
      document.getElementById("date").innerText = d.date;
    });
}

function updateYiyan() {
  const yiyan = document.getElementById("yiyan");
  yiyan.classList.add("fade");
  setTimeout(() => {
    fetch("/api/yiyan")
      .then((r) => r.json())
      .then((d) => {
        yiyan.innerText = d.yiyan || "……";
        yiyan.classList.remove("fade");
        yiyan.style.opacity = 1;
      })
      .catch(() => {
        yiyan.innerText = "获取失败";
        yiyan.classList.remove("fade");
        yiyan.style.opacity = 1;
      });
  }, 400);
}

function updateEmoji() {
  fetch("/api/mood")
    .then((r) => r.json())
    .then((d) => {
      const emoji = document.getElementById("emoji");
      emoji.src = "/emoji/" + d.mood + ".gif";
      const box = document.querySelector(".emoji-box");
      box.classList.add("shake");
      setTimeout(() => box.classList.remove("shake"), 500);
    });
}

function toggleFullScreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
}

function getWeatherIcon(desc) {
  // 简单映射，可根据需要扩展
  if (desc.includes("晴")) return "☀️";
  if (desc.includes("多云")) return "⛅";
  if (desc.includes("阴")) return "☁️";
  if (desc.includes("雨")) return "🌧️";
  if (desc.includes("雪")) return "❄️";
  if (desc.includes("雾")) return "🌫️";
  return "🌡️";
}

function updateWeather() {
  fetch("https://v.api.aa1.cn/api/api-tianqi-3/index.php?msg=宁波&type=1")
    .then((r) => r.json())
    .then((d) => {
      if (d.code === "1" && d.data && d.data.length > 0) {
        const today = d.data[0];
        document.getElementById("weather-icon").textContent = getWeatherIcon(
          today.tianqi
        );
        document.getElementById("weather-temp").textContent =
          today.wendu + "°C";
        document.getElementById("weather-desc").textContent = "PM:" + today.pm;
      } else {
        document.getElementById("weather-icon").textContent = "❓";
        document.getElementById("weather-temp").textContent = "--°C";
        document.getElementById("weather-desc").textContent = "获取失败";
      }
    })
    .catch(() => {
      document.getElementById("weather-icon").textContent = "❓";
      document.getElementById("weather-temp").textContent = "--°C";
      document.getElementById("weather-desc").textContent = "获取失败";
    });
}

function updateSensor() {
  fetch("/api/sensor")
    .then((r) => r.json())
    .then((d) => {
      if (d.temperature !== undefined && d.humidity !== undefined) {
        document.getElementById("sensor-temp").textContent =
          d.temperature + "°C";
        document.getElementById("sensor-humidity").textContent =
          d.humidity + "%";
      } else {
        document.getElementById("sensor-temp").textContent = "--°C";
        document.getElementById("sensor-humidity").textContent = "--%";
      }
    })
    .catch(() => {
      document.getElementById("sensor-temp").textContent = "--°C";
      document.getElementById("sensor-humidity").textContent = "--%";
    });
}

// 定时刷新
setInterval(updateTime, 1000);
setInterval(updateYiyan, 30000);
setInterval(updateEmoji, 10000);
setInterval(updateSensor, 5000); // 每5秒刷新一次温湿度
setInterval(updateWeather, 30 * 60 * 1000); // 半小时刷新一次

// 首次加载
updateTime();
updateYiyan();
updateEmoji();
updateWeather();
updateSensor();

// 双击全屏
document.body.ondblclick = toggleFullScreen;
