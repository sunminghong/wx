

//春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"

const fmtWords_old = function(classic, durPerLetter) {
    let ldata = [];
    let off= 0;
    let dur = 0;

    var defaultParseLine = function(off, line) {
        let end = off
        let arr = [];
        for (var i in line) {
            let w = line[i];
            end = off + durPerLetter;
            arr.push(w+","+ off + "," + end);
            off = end;
        }

        return [end, arr.join('|'), ls];
    }

    let ret = defaultParseLine(off,classic.title);
    off = ret[0];
    ldata.push(ret[1]);

    ret = defaultParseLine(off,classic.author);
    off = ret[0];
    ldata.push(ret[1]);

    let lls = classic.words.replace(/，/g,'，,').replace(/。/g,'。,').replace(/？/g,'？,').replace(/！/g,',')
        .split(',');
    console.log(lls);
    for (var i in lls) {
        let line = lls[i];
        if (line == "") continue;

        ret = defaultParseLine(off,line);
        off = ret[0];
        ldata.push(ret[1]);
        
    }

    let ss= ldata.join('\n');
    console.log(ss);

    return ss;
}

const fmtWords = function(classic, durPerLetter) {
    let ldata = [];
    let off= 0;
    let dur = 0;

    var defaultParseLine = function(off, line) {
        let end = off
        let arr = [];
        for (var i in line) {
            let w = line[i];
            end = off + durPerLetter;
            arr.push(w);
            off = end;
        }

        return [end, arr.join('|')];
    }

    //let lls = classic.replace(/，/g,'，,').replace(/。/g,'。,').replace(/？/g,'？,').replace(/！/g,',').split(',');
    
    let lls = classic.split('\n');
    console.log(lls);

    for (var i in lls) {
        let line = lls[i];
        if (line == "") continue;

        let ret = defaultParseLine(off,line);
        off = ret[0];
        ldata.push(ret[1]);
        
    }

    let ss= ldata.join('\n');
    console.log(ss);

    return ss;
}

module.exports = {
    fmtWords:fmtWords
}
