const util = require('../../utils/util.js')

//春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"
//lyrics
//rime
const read = function (durPerStep, stepPerLetter, pageData, pageSetDatafn, cb_show, cb_finish) {
  this.durPerStep = durPerStep;
  this.stepPerLetter = stepPerLetter;
  this.pageData = pageData;
  this.setData = pageSetDatafn;

  this.cb_show = cb_show;
  this.cb_finish = cb_finish;


    //每行默认休止多少个step
   this.lineStopStep = 30;
    //每个休止符等于多少个step，默认约16*30 ms，
   this.stopCharStep = 16;

  //存放解析好的文字播放数据
  this.ldata = [];

  this._pIdx = 0;
  this.termStepCount = 0;
}

let $fn = read.prototype;

$fn.getData = function (key) {
  return this.pageData[key];
}

$fn.init = function (classic, cb) {
  this.cb_show = cb || this.cb_show;

  let off = 0;
  let dur = 0;

  let wh = util.getScreenWH();
  let ww = wh[0];
  let hh = wh[1];

  //第多少个字
  let widx = 0;
  //第几行了（一句话超过宽度换行要+1）
  let lineIdx = -1;

  let self = this;
  let wcss = {};

  var defaultParseLine = function (off, line) {
    let ldata = self.ldata;
    lineIdx++;

    //let terms = [];
    let arr = [[]];
    let lls = line.split('|');
    let ar = arr[0];

    let llslen = lls.length;
    for (let i=0; i<llslen;i++) {
      let w = lls[i];
      if (w == '') continue;

      let css ="word";
      let term = [];

          term = w.split(',');


          //红,0,300|鸟,300,700... (词,start,end)
          //如果不是以上这样的词谱格式就累计时刻值
          if (term.length < 3) {
            let dur = self.stepPerLetter;
            if (term.length == 2) { //红/hong,300|鸟...(字/拼音,dur)
              dur = parseInt(term[1]);
              term[1] = off;
            } else {
              term.push(off);
            }

            off += dur;
            term.push(off);
          }

          let z = term[0].split('/');
          if (z.length == 1) 
            z.push('');
          term = [widx, z[0], z[1], term[1], term[2], lineIdx];

      //"-" 是休止符，每一个“-”16个step ，约半秒
      if (i< llslen-1 && lls[i+1] == '-') {
          //term = [widx,"...","", off, off + self.stopCharStep, lineIdx];
          off += self.stopCharStep * w.length;

          term[4] = off
          i++;
      }

      ldata.push(term);

      ar.push([term[0], term[1], term[2], css]);

      if ((i * 1 + 1) % 8 == 0) {
        arr.push([]);
        ar = arr[arr.length - 1];
        lineIdx++;
      }

      wcss[widx] = 0;
      widx++;
    }

    //每一行结束是否增加一些延时（停顿）。
    ldata.push([widx,'','',off,off+self.lineStopStep, lineIdx]);
    off += self.lineStopStep;
    wcss[widx] = 0;
    //ar.push([widx,'','','linestart']);
    widx ++;


    return [off, arr];
  }

  let lls = classic.split('\n');
  console.log(lls);

  let lines = [];
  let title = [];
  let author = [];
  for (var i in lls) {
    let line = lls[i];
    if (line == "") continue;

    let ret = defaultParseLine(off, line);
    off = ret[0];

    if (i == 0)
      title = ret[1][0];
    else if (i == 1)
      author = ret[1][0];
    else {
      for (var jj in ret[1])
        lines.push(ret[1][jj]);
    }

    //ldata.push(ret[1]);
  }
    
  this.setData({
      "wcss":wcss
  });

  this.cb_show & this.cb_show(title, author, lines);
};


//////////////////////////////////////////////////////////////////////////
//start write kala-ok
//////////////////////////////////////////////////////////////////////////



$fn.play = function (cb, durPerStep) {
  this.durPerStep = durPerStep || this.durPerStep;
  this.cb_finish = cb || this.cb_finish;

  //播放到第几个字了
  this._pIdx = 0;

  //帧计数
  this._stepCount = 0;

  let self = this;

  // 启动单个字推进的定时器
  this.timer = setInterval(function () { self._play() }, this.durPerStep);
}


$fn._play = function () {
  let term = this.ldata[this._pIdx];
  this.termStepCount += 1;
  let termStep = term[4] - term[3];
  let ppp = parseInt(this.termStepCount * 100 / termStep);

  let data = this.getData("wcss");
  data[term[0]] = ppp<20 ? 20:ppp;

  this.setData({
    wcss: data
  })

  if (this.termStepCount == termStep) {
    this.termStepCount = 0;
    this._pIdx++;

    //结束了,回调
    if (this._pIdx >= this.ldata.length) {
      clearInterval(this.timer);
      this.timer = null;

      this.cb_finish();
    }
  }
}

$fn.reStart = function(durPerStep) {
  this.durPerStep = durPerStep || this.durPerStep;

  clearInterval(this.timer);

  // 启动单个字推进的定时器
  this.timer = setInterval(function () { self._play() }, this, this.durPerStep);
}


$fn.pause = function() {
  clearInterval(this.timer);
}



module.exports = {
  read: read
}
