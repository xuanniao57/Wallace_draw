import { readFile, mkdir, writeFile } from "node:fs/promises";
import { resolve, join } from "node:path";
import { createRequire } from "node:module";
import { csvParse, geoIdentity, geoPath, scaleThreshold, scaleLinear, descending, format } from "d3";
import { feature } from "topojson-client";

const require = createRequire(import.meta.url);
const csv = await readFile(new URL("../assets/resident-population.csv", import.meta.url), "utf8");
const rows = csvParse(csv, r => {
  const before = Number(r.resident_2010);
  const after = Number(r.resident_2020);
  if (!Number.isInteger(before) || !Number.isInteger(after) || before <= 0 || after <= 0) {
    throw Error("Invalid population count for " + r.state);
  }
  return {name: r.state, gain: after - before, rate: 100 * (after - before) / before};
});
const topo = JSON.parse(await readFile(require.resolve("us-atlas/states-albers-10m.json"), "utf8"));
const states = feature(topo, topo.objects.states).features.filter(s =>
  !["11", "72", "60", "66", "69", "78"].includes(s.id)
);
const values = new Map(rows.map(r => [r.name, r]));
if (rows.length !== 50 || values.size !== 50 || states.length !== 50 ||
    new Set(states.map(s => s.properties.name)).size !== 50 ||
    states.some(s => !values.has(s.properties.name))) throw Error("Expected 50 unique matched states");

const colors = ["#b76736", "#e4ede9", "#b4d3c7", "#6da390", "#246353"];
const color = scaleThreshold([0, 5, 10, 15], colors);
const ink = "#1e332f", muted = "#4c605a", rule = "#ced8d3";
const zh = {Utah:"犹他", Idaho:"爱达荷", Texas:"得州", "North Dakota":"北达科他",
  Nevada:"内华达", California:"加利福尼亚", Florida:"佛罗里达", Georgia:"佐治亚",
  Washington:"华盛顿", Colorado:"科罗拉多", Arizona:"亚利桑那", "North Carolina":"北卡罗来纳"};
const rank = key => rows.slice().sort((a,b) => descending(a[key], b[key]) || a.name.localeCompare(b.name));
const rateRank = rank("rate"), gainRank = rank("gain");
const rateLeader = rateRank[0], gainLeader = gainRank[0];
const out = resolve(process.argv[2] || "rendered");
const xml = s => String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
const nameOf = r => zh[r.name] || r.name;
const line = (x1,y1,x2,y2,stroke=rule,width=1) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${width}"/>`;
const label = (x,y,content,size=16,opts={}) =>
  `<text x="${x}" y="${y}" font-size="${size}" fill="${opts.fill || ink}" font-weight="${opts.weight || 400}" text-anchor="${opts.anchor || "start"}">${xml(content)}</text>`;
const parts = [];
const title = `${nameOf(rateLeader)}人口增速最快，${nameOf(gainLeader)}新增人口最多`;
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="110mm" viewBox="0 0 900 550" role="img" aria-labelledby="title desc"><title id="title">${title}</title><desc id="desc">2010 至 2020 年美国五十州常住人口变化。地图显示增长率，两个点图分别按增长率和新增人口取前五。</desc><rect width="900" height="550" fill="white"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif">`);
parts.push(label(24,42,title,31,{weight:700}), label(25,73,"美国 50 州常住人口变化  /  2010–2020",17,{fill:muted}), line(24,91,876,91,ink));
const panel = (letter,x,y,text) => label(x,y,letter,18,{weight:700,fill:"#246353"}) + label(x+25,y,text,18,{weight:700});
parts.push(panel("a",24,125,"州人口增长率"), panel("b",567,125,"增长率前五"), panel("c",567,330,"新增人口前五"));
const path = geoPath(geoIdentity().fitExtent([[26,145],[535,416]], {type:"FeatureCollection",features:states}));
for (const s of states) {
  const value = values.get(s.properties.name);
  parts.push(`<path id="state-${s.id}" d="${path(s)}" fill="${color(value.rate)}" stroke="#687e75" stroke-width="0.55"><title>${xml(value.name)} · ${value.rate.toFixed(2)}%</title></path>`);
}
for (const row of [rateLeader, gainLeader]) {
  const state = states.find(s => s.properties.name === row.name);
  const [x,y] = path.centroid(state);
  parts.push(label(x,y+4,nameOf(row),13,{weight:700,anchor:"middle",fill:"#ffffff"}));
}
const legend = ["<0", "0–<5", "5–<10", "10–<15", "≥15"];
parts.push(label(26,447,"增长率（%）",15,{weight:700}));
colors.forEach((c,i) => {
  const x = 32 + 98*i;
  parts.push(`<rect x="${x}" y="458" width="90" height="11" fill="${c}"/>`,label(x+45,489,legend[i],15,{anchor:"middle"}));
});
function rankedPanel(data, key, top, maximum, suffix) {
  const scale = scaleLinear([0,maximum],[660,813]);
  parts.push(label(875,top-21,suffix,14,{anchor:"end",fill:muted}));
  data.slice(0,5).forEach((r,i) => {
    const y = top + 24*i;
    const v = key === "rate" ? r.rate : r.gain / 10000;
    const x = scale(v);
    parts.push(label(567,y+5,nameOf(r),15),line(scale(0),y,scale(maximum),y,rule),
      line(scale(0),y,x,y,"#85aa9d",2),
      `<circle cx="${x}" cy="${y}" r="4.5" fill="#246353"/>`,
      label(875,y+5,v.toFixed(1),15,{anchor:"end",weight:i===0?700:400}));
  });
  [0, maximum/2, maximum].forEach(t => parts.push(label(scale(t),top+122,format("~g")(t),13,{anchor:"middle",fill:muted})));
}
rankedPanel(rateRank,"rate",161,20,"%");
rankedPanel(gainRank,"gain",366,400,"万人");
parts.push(line(24,505,876,505),label(25,530,"来源：美国人口普查局，2010、2020 年普查；州界为 2017 年制图边界。阿拉斯加与夏威夷置于插图位置。",14,{fill:muted}),"</g></svg>");
await mkdir(out,{recursive:true});
await writeFile(join(out,"population-change.svg"),parts.join("\n")+"\n");
console.log(`Wrote 50 matched states and two rankings to ${out}`);
