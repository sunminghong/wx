//app.js
var timestamp = Date.parse(new Date());
timestamp = timestamp / 1000;  

App({
  globalData:{
    showapi_sign:'844e06d697e04e9dbd3c52286c89a69a',
    showapi_appid: 66173,
    maxResult:10,
    showapi_timestamp: timestamp,
  }
})