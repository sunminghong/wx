const util = require('util.js')

//春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"
//lyrics 歌词；peotry 诗词、韵文；recite 吟咏、背诵；
//rime
class PoetryHelper {

  constructor(param) {
    this.durPerStep = param.durPerStep;
    this.stepPerLetter = param.stepPerLetter;
    this.pageData = param.pageData;
    this._setData = param.fn_pageSetData;

    this.cb_show = param.cb_show;
    this.cb_finish = param.cb_finish;


    //每行默认休止多少个step
    this.lineStopStep = 30;
    //每个休止符等于多少个step，默认约16*30 ms，
    this.stopCharStep = 16;

      this._gres_css= "gres_";

    this._defaultWordCss = "word";

    //存放解析好的文字播放数据
    this.ldata = [];

    this._pIdx = 0;
    this.termStepCount = 0;
  }

  _getData(key) {
    return this.pageData[key];
  }

  //let classic = "春晓\n王维\n春眠不觉晓，\n处处闻啼鸟。\n夜来风雨声，\n花落知多少。";
  //let classic = "春|晓\n王,400|维\n春|眠|不|觉|晓|，\n处|处|闻|啼|鸟|。\n夜|来|风|雨|声|，\n花|落|知|多|少|。";
  //let classic = "春|晓\n作|者|：|王|维\n春|眠|-|不|觉|晓|\n处|处|-|闻|啼|鸟\n夜|来|-|风|雨|声\n花|落|-|知|多|少";
  parse(classic, cb) {
    this.cb_show = cb || this.cb_show;

    let off = 0;
    let dur = 0;

    let wh = util.getScreenWH();
    let ww = wh[0];
    let hh = wh[1];
    let termsPerline = parseInt(ww / 90);

    //第多少个字
    let widx = 0;
    //第几行了（一句话超过宽度换行要+1）
    let lineIdx = 0;

    let self = this;
    let wcss = {};



    let defaultParseLine = function (off, line) {
      lineIdx++;

      //let terms = [];
      let arr = [[]];
      let lls = line.split('|');
      let ar = arr[0];
      let ldata = self.ldata;
      let row = [];

      let llslen = lls.length;
      for (let i = 0; i < llslen; i++) {
        let w = lls[i];
        if (w == '') continue;

        let css = self._defaultWordCss;
        let term = [];

        term = w.split(',');


        //如果不是以上这样的词谱格式就累计时刻值
        let dur = self.stepPerLetter;
        if (term.length == 2) { //红/hong,300|鸟...(字/拼音,dur)
          dur = parseInt(term[1]);
          term[1] = off;
        } else {
          term.push(off);
        }

        off += dur;
        term.push(off);

        let z = term[0].split('/');
        if (z.length == 1)
          z.push('');
        term = [widx, z[0], z[1], term[1], term[2], lineIdx];

        //"-" 是休止符，每一个“-”16个step ，约半秒
        if (i < llslen - 1 && lls[i + 1] == '-') {
          //term = [widx,"...","", off, off + self.stopCharStep, lineIdx];
          off += self.stopCharStep * w.length;

          term[4] = off
          i++;
        }

        row.push(term);

        ar.push([term[0], term[1], term[2], css]);

        if ((i * 1 + 1) % termsPerline == 0) {
          arr.push([]);
          ar = arr[arr.length - 1];
          lineIdx++;
        }

        wcss[widx] = 0;
        widx++;
      }

      //每一行结束是否增加一些延时（停顿）。
      row.push([widx, '', '', off, off + self.lineStopStep, lineIdx]);
      off += self.lineStopStep;
      wcss[widx] = 0;
      //ar.push([widx,'','','linestart']);
      widx++;

      ldata.push(row);

      return [off, arr];
    }

    let lls = classic.split('\n');
    console.log(lls);

    let lines = [];
    let llslen = lls.length;



    let row = [];
    let ar = [];
    //开头数3、2、1
    row.push([widx, '▶︎', '', off, off + self.durPerStep, lineIdx]);
    off += self.durPerStep;
    wcss[widx] = 0;
    ar.push([widx, '▶︎', '', self._defaultWordCss]);
    widx++;

    row.push([widx, '▶︎', '', off, off + self.durPerStep, lineIdx]);
    off += self.durPerStep;
    wcss[widx] = 0;
    ar.push([widx, '▶︎', '', self._defaultWordCss]);
    widx++;

    row.push([widx, '▶︎', '', off, off + self.durPerStep, lineIdx]);
    off += self.durPerStep;
    wcss[widx] = 0;
    ar.push([widx, '▶︎', '', self._defaultWordCss]);
    widx++;

    this.ldata.push(row);

    let begin = { css: "begin", term: ar }

    for (let i = 0; i < llslen; i++) {
      let line = lls[i];
      if (line == "") continue;

      let ret = defaultParseLine(off, line);
      off = ret[0];

      if (i == 0)
        lines.push({ css: "title", term: ret[1][0] });
      else if (i == 1)
        lines.push({ css: "author", term: ret[1][0] });
      else {
        for (var jj in ret[1])
          lines.push({ css: "", term: ret[1][jj] });
      }
    }

    this.wcss = wcss;
    this._setData({
      "wcss": wcss
    });

    this.cb_show & this.cb_show(begin, lines);
  }


  //////////////////////////////////////////////////////////////////////////
  //start write kala-ok
  //////////////////////////////////////////////////////////////////////////


  //ifFollow 是否是跟随模式（每句显示两遍）
  play(ifFollow, durPerStep, cb) {
    if (this.timer) {
        if (this.durPerStep == durPerStep) {
            return;
        }
        clearInterval(this.timer);
    }

    this.ifFollow = ifFollow;
    this.durPerStep = durPerStep || this.durPerStep;
    this.cb_finish = cb || this.cb_finish;

    if ((this._pIdx && this._pIdx>0) || (this._lineIdx && this._lineIdx>0))
          this.clearProgress();

    //播放到该行/句第几个字了
    this._pIdx = 0;
      //播放到第几行了
    this._lineIdx = 0;
      //总播放了多少行;
    this._playLines = 0;

    //帧计数
    this._stepCount = 0;

    let self = this;

    // 启动单个字推进的定时器
    this.timer = setInterval(function () { self._play() }, this.durPerStep);
  }

  _play() {
    let term = this.ldata[this._lineIdx][this._pIdx];
    this.termStepCount += 1;
    let termStep = term[4] - term[3];
    let ppp = parseInt(this.termStepCount * 100 / termStep);

    //let data = this._getData("wcss");
    this.wcss[term[0]] = this._gres_css + (ppp < 20 ? 20 : ppp);

    this._setData({
      wcss: this.wcss 
    })

    if (this.termStepCount == termStep) {
      this.termStepCount = 0;
      this._pIdx++;

        //换下一行
      if (this._pIdx >= this.ldata[this._lineIdx].length) {
          //如果是跟读模式应该读两遍
          if (this.ifFollow && this._playLines % 2 == 0) {
              this._gres_css = "gres_f_";
          } else {
              this._lineIdx ++;
          }
          
          this._playLines ++;
          this._pIdx = 0;


          //结束了,回调
          if (this._lineIdx >= this.ldata.length) {
            clearInterval(this.timer);
            this.timer = null;

            this.cb_finish();
          }
      }
    }
  }

  continue() {
      if (this.timer) return;
    clearInterval(this.timer);
    // 启动单个字推进的定时器
    this.timer = setInterval(function () { self._play() }, this, this.durPerStep);
  }


  pause() {
    clearInterval(this.timer);
      this.timer = null;

  }

  clearProgress() {
      let wcss = this.wcss;

      for(let i in wcss) {
          wcss[i]=0;
      }
  }
}



module.exports = {
  PoetryHelper: PoetryHelper
}
