const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

//正则判断
function Regular(str, reg) {
  if (reg.test(str))
    return true;
  return false;
}

//是否为中文
function IsChinese(str) {
  var reg = /^[\u0391-\uFFE5]+$/;
  return Regular(str, reg);
}


//取得屏幕宽高，单位微rpx
function getScreenWH() { 
    try {
      var res = wx.getSystemInfoSync()
      console.log(res.model)
      console.log(res.pixelRatio)
      console.log('width:',res.windowWidth)
      console.log(res.windowHeight)
      console.log(res.language)
      console.log(res.version)
      console.log(res.platform)
      return [res.pixelRatio * res.windowWidth, res.pixelRatio * res.windowHeight]
    } catch (e) {
      return [750, 1334]
    }
}


module.exports = {
  formatTime: formatTime,
  isChinese: IsChinese,
  getScreenWH:getScreenWH
}
