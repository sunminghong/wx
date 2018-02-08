const drawkrc = _etext => {
  /*
  krc歌词解析目标格式要求
  var lines = [{'ws':[{'w':word, 'o':offset, 'd':duration},{'w':word, 'o':offset, 'd':duration},...], 'o':offset, 'd':duration},
         {'ws':[{'w':word, 'o':offset, 'd':duration},{'w':word, 'o':offset, 'd':duration},...], 'o':offset, 'd':duration},
         ...]
  */
  //一下是模拟krc解析后的歌词数据
  var lines = [];
  var offset = 0;
  var duration = 0;
  for (var i = 0; i < 1000; i++) {
    duration = 7400;
    lines.push({ 'ws': [{ 'w': "这", 'o': 0, 'd': 300 }, { 'w': "是", 'o': 300, 'd': 400 }, { 'w': "歌", 'o': 700, 'd': 200 }, { 'w': "词", 'o': 900, 'd': 500 }, { 'w': "测", 'o': 1900, 'd': 100 }, { 'w': "试", 'o': 2000, 'd': 400 }, { 'w': "，", 'o': 2400, 'd': 800 }, { 'w': "请", 'o': 3200, 'd': 1200 }, { 'w': "关", 'o': 4400, 'd': 1000 }, { 'w': "注", 'o': 5400, 'd': 200 }, { 'w': "效", 'o': 5600, 'd': 1600 }, { 'w': "果", 'o': 7200, 'd': 200 }], 'o': offset, 'd': duration });
    offset += 7400;
    duration = 7300;
    lines.push({ 'ws': [{ 'w': "经", 'o': 0, 'd': 200 }, { 'w': "测", 'o': 200, 'd': 500 }, { 'w': "试", 'o': 700, 'd': 200 }, { 'w': "，", 'o': 900, 'd': 1000 }, { 'w': "网", 'o': 1900, 'd': 200 }, { 'w': "页", 'o': 2100, 'd': 500 }, { 'w': "的", 'o': 2600, 'd': 200 }, { 'w': "效", 'o': 2800, 'd': 300 }, { 'w': "果", 'o': 3900, 'd': 300 }, { 'w': "也", 'o': 4200, 'd': 100 }, { 'w': "还", 'o': 4300, 'd': 300 }, { 'w': "不", 'o': 5700, 'd': 600 }, { 'w': "错", 'o': 6300, 'd': 1000 }], 'o': offset, 'd': duration });
    offset += 7300;
  }

  /*
  将解析后的一行歌词添加到dom中
  */
  //var _etext = document.getElementById("text");
  var wstoes = function (words) {
    var ps = "";
    for (var i = 0; i < words.length; i++) {
      ps += "<p>" + words[i]['w'] + "</p>";
    }
    _etext.innerHTML = ps;

    var _eps = _etext.getElementsByTagName("p");
    for (var i = 0; i < words.length; i++) {
      _eps[i].offset = words[i]['o'];
      _eps[i].duration = words[i]['d'];
    }
    return _eps;
  }


  var step = 30; // 默认刷新时长30ms，刷新时长配置对桌面歌词性能影响较大
  var timer; // 启动单个字推进的定时器
  /*
  处理单个显示元素
  _eps: dom节点列表，表示歌词中单个显示元素
  _index: 当前变化元素的索引
  _ps: process step，每次timeout推进的步长
  _process: 当前变化元素的进度（0-100）
  pos: 对该元素进行处理时间点，在哪个timeout点处理
  count: timeout的次数
  */
  var _processw = function (_eps, _index, _ps, _process, pos, count) {
    _ep = _eps[_index];
    if (count >= pos) {
      _process += _ps;
      _ep.style.backgroundImage = "-webkit-linear-gradient(top, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0) 100%), -webkit-linear-gradient(left, #f00 " + _process + "%, #00f 0%)";

      if (_process >= 99) {
        if ((_index + 1) >= _eps.length) { //该句结束退出
          return;
        }
        _index++;
        var ts = Math.round(_eps[_index].duration / step) == 0 ? 1 : Math.round(_eps[_index].duration / step);
        _ps = 100 / ts;
        _process = 0;
        pos = Math.round(_eps[_index].offset / step);
      }
    }
    count++;
    timer = setTimeout(_processw.bind(this, _eps, _index, _ps, _process, pos, count), step);
  }

  /*
  处理单行
  */
  var _processL = function (words) {
    var _eps = wstoes(words);
    clearTimeout(timer); //清除上一行因为页面渲染延迟没有处理完的定时器
    _processw(_eps, 0, 100 / Math.round(_eps[0].duration / step), 0, Math.round(_eps[0].offset / step), 0);
  }

  /*
  处理全部krc歌词
  */
  var timers = [];
  var _processK = function () {
    for (var i = 0; i < lines.length; i++) {
      var timer = setTimeout(_processL.bind(this, lines[i]['ws']), lines[i]['o']);
      timers.push(timer);
    }
  }

  //启动处理
  _processK();


  ///////////////////////////////////////////////////////
  // 下面是一些用户操作响应
  /*
  document.getElementById("text").addEventListener("mousedown", winmove, false);
  document.getElementById("bigger").addEventListener("click", bigger, false);
  document.getElementById("smaller").addEventListener("click", smaller, false);
  document.getElementById("lock").addEventListener("click", lock, false);
  document.getElementById("close").addEventListener("click", close, false);
      */
  function winmove(_Event) {
    channel.Call('winctrl.dragWindow');
  }
  /*
  字体变大
  */
  var fontsize = 60;
  function bigger(_Event) {
    if (fontsize < 80) {
      fontsize += 2;
      var font = "normal normal bold " + fontsize + "px 微软雅黑,sans-serif"
      _etext.style.font = font;
    }
  }
  /*
  字体变小
  */
  function smaller(_Event) {
    if (fontsize > 16) {
      fontsize -= 2;
      var font = "normal normal bold " + fontsize + "px 微软雅黑,sans-serif"
      _etext.style.font = font;
    }
  }
  /*
  窗口锁定，在PC混合应用容器中有效
  */
  function lock(_Event) {
    if (typeof (channel) == "undefined") {
      alert("窗口锁定功能只在pc混合应用容器中有效");
    } else {
      channel.Call('winctrl.lockwindow');
    }
  }
  /*
  窗口关闭，在PC混合应用容器中有效
  */
  function close(_Event) {
    if (typeof (channel) == "undefined") {
      alert("窗口关闭功能只在pc混合应用容器中有效");
    } else {
      channel.Call('winctrl.sendMessage', [{ "src": "lrc", "action": "close" }]);
    }

  }
}



module.exports = {
  drawkrc: drawkrc
}
