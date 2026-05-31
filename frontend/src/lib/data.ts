import type {
  Character,
  Novel,
  Scene,
  Option,
  CharacterProfile,
  SleepLog,
  Turn,
} from "./types";

export const NMA_NOVEL: Novel = {
  title: "Frankenstein",
  author: "Mary Shelley",
  year: 1818,
  chapters: 24,
  emoji: "📖",
};

export const NMA_CHARACTERS: Character[] = [
  {
    id: "victor",
    name: "Victor Frankenstein",
    emoji: "🧠",
    role: "Protagonist · Creator",
    confidence: 0.73,
    status: "consolidated",
    flag: "⚡ 1 unresolved conflict",
  },
  {
    id: "creature",
    name: "The Creature",
    emoji: "🌑",
    role: "The Created",
    confidence: 0.81,
    status: "consolidated",
  },
  {
    id: "elizabeth",
    name: "Elizabeth Lavenza",
    emoji: "🌹",
    role: "Betrothed",
    confidence: 0.66,
    status: "consolidated",
  },
  {
    id: "henry",
    name: "Henry Clerval",
    emoji: "🎭",
    role: "Closest friend",
    confidence: 0.58,
    status: "forming",
  },
  {
    id: "walton",
    name: "Robert Walton",
    emoji: "🧭",
    role: "Frame narrator",
    confidence: 0.41,
    status: "forming",
  },
];

export const NMA_SCENE: Scene = {
  eyebrow: "📖 场景 · 第17章，冰海",
  text: "冰川之上，造物追上了你。他要你造一个伴侣——雌性——并发誓一旦拥有，便带着她消失在南美荒野，再不扰世人。",
  question: "如果你是Victor——你会怎么做？",
};

export const NMA_OPTIONS: Option[] = [
  {
    idx: "Direction 01",
    title: "断然拒绝，独自下冰川",
    voice: "“我不会为了平息一个诅咒，就把第二个诅咒放到世上。你要追便追。”",
    tag: "✅ 吻合：压力下的回避",
    tagNew: false,
    risk: { level: "low", label: "✅ 贴合", pct: 12 },
  },
  {
    idx: "Direction 02",
    title: "假意答应——暗中准备毁掉造物",
    voice: "“让他以为我答应了。我的手不必诚实，只要忙碌。”",
    tag: "✅ 吻合：隐瞒 · 拖延",
    tagNew: false,
    risk: { level: "low", label: "✅ 贴合", pct: 24 },
  },
  {
    idx: "Direction 03",
    title: "谈条件——质问他的真实意图",
    voice: "“我怎么知道你的同类会安分守在荒野，而不是繁衍出一个对抗我们的种族？”",
    tag: "🆕 新方向 · 证据不足",
    tagNew: true,
    risk: { level: "med", label: "⚠️ 偏移", pct: 49 },
  },
  {
    idx: "Direction 04",
    title: "当场动手——在冰川上拼了",
    voice: "“我就在这里了结你，哪怕这座山把我们俩一起埋了。”",
    tag: "❌ 违背：回避直面冲突",
    tagNew: false,
    risk: { level: "high", label: "❌ 崩人设", pct: 81 },
  },
];

export const NMA_FOLLOWUP: { options: Option[] } = {
  options: [
    {
      idx: "Direction 01",
      title: "埋头工作，不告诉任何人",
      voice: "“我会独自承担，就像我承担我造出的每一片废墟那样。”",
      tag: "✅ 吻合：负罪式隐瞒",
      tagNew: false,
      risk: { level: "low", label: "✅ 贴合", pct: 18 },
    },
    {
      idx: "Direction 02",
      title: "向Elizabeth坦白一切，寻求她的建议",
      voice: "“也许有一个人知道真相，这重量就不会压垮我。”",
      tag: "🆕 冲突：与已有的隐瞒模式不符",
      tagNew: true,
      risk: { level: "med", label: "⚠️ 偏移", pct: 53 },
    },
    {
      idx: "Direction 03",
      title: "直接去找法官自首",
      voice: "“抓我吧，审判我吧——只求这件事由别人的手来阻止。”",
      tag: "❌ 违背：害怕不被相信 · 骄傲",
      tagNew: false,
      risk: { level: "high", label: "❌ 崩人设", pct: 74 },
    },
  ],
};

export const NMA_PROFILE: Record<string, CharacterProfile> = {
  victor: {
    traits: [
      { name: "🧠 智识自负", conf: 0.88, evidence: 11, isNew: false },
      { name: "🙈 压力下回避", conf: 0.81, evidence: 7, isNew: false },
      { name: "🤐 负罪式隐瞒", conf: 0.79, evidence: 6, isNew: false },
      { name: "🛡️ 对家人的保护欲", conf: 0.72, evidence: 4, isNew: true },
      { name: "🏔️ 对崇高的敬畏", conf: 0.61, evidence: 5, isNew: false },
    ],
    patterns: [
      { cond: "面对造物时", body: "退缩、拖延或隐瞒，而非行动。", strength: 4 },
      { cond: "无辜者遇险时", body: "事后自责；极少提前阻止。", strength: 3 },
      { cond: "身处群山或风暴中时", body: "平静下来，恢复决心。", strength: 3 },
      { cond: "被权威质问时", body: "隐瞒真相，害怕不被相信。", strength: 2 },
    ],
    relationships: [
      { id: "victor", name: "Victor", emoji: "🧠", rel: "自己", x: 50, y: 50, center: true, tone: "" },
      { id: "elizabeth", name: "Elizabeth", emoji: "🌹", rel: "未婚妻", x: 50, y: 14, tone: "warm" },
      { id: "henry", name: "Henry", emoji: "🎭", rel: "挚友", x: 84, y: 34, tone: "warm" },
      { id: "creature", name: "造物", emoji: "🌑", rel: "造物·宿敌", x: 82, y: 76, tone: "fraught" },
      { id: "william", name: "William", emoji: "🕊️", rel: "亡弟", x: 18, y: 76, tone: "grief" },
      { id: "alphonse", name: "Alphonse", emoji: "👴", rel: "父亲·责任", x: 16, y: 34, tone: "warm" },
    ],
  },
};

export const NMA_LOG: SleepLog = {
  cycle: 14,
  ranAt: "03:12",
  duration: "41s",
  confBefore: 0.65,
  confAfter: 0.73,
  phases: [
    {
      n: 1,
      title: "💤 事实巩固",
      sub: "将近期阅读的原始事件折叠为稳定记忆。",
      entries: [
        { tag: "extract", text: "从第5-7章提取了 3 个冲突回避事件 → 更新Victor的行为模式。" },
        { tag: "conflict", text: "检测到 1 个矛盾：Victor在第20章发誓毁灭造物，与已有的回避模式冲突——标记未解决。" },
        { tag: "trait", text: "新增特质「🛡️ 对家人的保护欲」(置信度 0.72)。" },
      ],
    },
    {
      n: 2,
      title: "🧩 抽象整合",
      sub: "将具体事件压缩为可复用的行为规则。",
      entries: [
        { tag: "extract", text: "识别出模式：Victor面对强大或超自然的力量时退缩，但在无辜者遇险时会行动。" },
        { tag: "prune", text: "剪枝了 5 个低权重无关事件。" },
        { tag: "extract", text: "情感解耦：将「恐惧」从具体场景中剥离，关联到「超自然」语义节点。" },
      ],
    },
    {
      n: 3,
      title: "🔍 自检报告",
      sub: "Agent审视自己对角色的认知模型。",
      entries: [
        { tag: "trait", text: "角色置信度：0.65 → 0.73 📈" },
        { tag: "conflict", text: "未解决冲突：1 个——回避 vs 保护欲。这是角色弧光的潜在方向。" },
      ],
    },
  ],
  suggestion:
    "下一章，让Victor面临一个无法同时回避造物和保护家人的选择——把这个矛盾逼到明面上来。",
};

export function freshConvo(): {
  chosen: number | null;
  feedback: string | null;
  note: string;
  submitted: boolean;
  turns: Turn[];
  thinking: boolean;
} {
  return {
    chosen: null,
    feedback: null,
    note: "",
    submitted: false,
    turns: [],
    thinking: false,
  };
}
