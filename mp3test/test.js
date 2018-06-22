 function computeVolume(view) {
  const r = view.length;

  //const view=new Int8Array(frameBuffer);
  let pw = 0, v = 0;
  //将缓冲区内容按字节求平方和
  for (let i = 0; i < r; i++) {
    const c = view[i];

    v += c * c;

    let s = Math.max(-1, Math.min(1, c * 8));//PCM 音量直接放大8倍，失真还能接受
    s = s < 0 ? s * 0x8000 : s * 0x7FFF;
    pw += Math.abs(s);
  }
  //const mean = v / r;
  const mean = Math.floor(Math.abs(Math.floor(v /r)/10000) >> 1);
  const volume = 10 * Math.log10(mean);
  console.log('bytes:', r, "v:", v, "mean:", mean, "volume:", volume);

  //求平均值，得到音量大小
  const power = pw / r;
  //计算分贝值
  let powerLevel = 0;
  if (power > 0) {
    //https://blog.csdn.net/jody1989/article/details/73480259
    powerLevel = Math.round(Math.max(0, (20 * Math.log10(power / 0x7fff) + 34) * 100 / 34));
  };

  //const volume = 10*Math.log10(mean);
  console.log('bytes:', r, "power:", power, "volume:", powerLevel);

}

//let asset = AV.Asset.fromBuffer(frameBuffer);
let asset = AV.Asset.fromURL('http://127.0.0.1:8081/song.mp3');
var list = new Float32Array();
let vv = 0;

asset.on('error', function (e) {
  console.log('mp3 asset err:', e);
});
asset.on('data', function(buffer) {
  //list.push(buffer);
   vv +=buffer.byteLength;
 });
asset.on('end', function(buffer) {

  console.log("vv:", vv);
 });
asset.start();

console.log("vv:", vv);

/*
const that = this;

try {
  asset.decodeToBuffer(function (buffer) {
    // buffer is now a Float32Array containing the entire decoded audio file
    console.log("000vv:", vv);
    vv += buffer.byteLength;
    that.computeVolume(buffer); //调用_visualize进行下一步处理，此方法在后面定义并实现
    that.isDecoding = false;
  });
} catch (e) {
  that.isDecoding = false;
  console.log(e);
}
*/

