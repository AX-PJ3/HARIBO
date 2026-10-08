#!/usr/bin/env python3
"""team-wiki에서 기준을 읽어, 실제 Linear 이슈와 이어 샘플 데이터(변경 → 확인할 변경 → 응답)를 만든다."""
import csv, json, re, sys
from pathlib import Path

WIKI = Path(sys.argv[1]); OUT = Path(sys.argv[2]); (OUT / "data").mkdir(parents=True, exist_ok=True)

# ---------- 1. 위키 읽기
AREA_NAME = {"goal": "문제와 목표", "wiki": "기준 모으기", "detect": "바뀐 기준 찾기", "notify": "알리기",
             "app": "앱 화면", "data": "데이터 구조", "copy": "문구", "work": "일하는 방식"}
standards = {}
for p in sorted(WIKI.glob("*.md")):
    cur = None
    for line in p.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^###\s+(\S+)$", line)
        if h:
            cur = {"id": h.group(1), "area": h.group(1).split(".")[0], "file": p.name}
            standards[cur["id"]] = cur; continue
        if line.startswith("#"): cur = None; continue
        f = re.match(r"^-\s*([^:]+?)\s*:\s*(.*)$", line)
        if cur and f: cur[f.group(1).strip()] = f.group(2).strip()

# ---------- 2. 사람과 이슈 (실제 Linear)
PEOPLE = ["호윤", "정민", "경하", "민수", "부건", "신지"]
ISSUES = {  # 번호: (제목, 담당, 상태)
 "SIL-28": ("[알리기] v0 켤 때 바뀐 기준 보여 주고 답 기록하기", "민수", "진행 중"),
 "SIL-31": ("[알리기] 응답 기록과 표로 내보내기", "민수", "진행 중"),
 "SIL-32": ("[알리기] 앱 알림: 실시간 변경 받기, Mac·Windows 알림", "민수", "할 일"),
 "SIL-34": ("[알리기] 터미널 알림 첫 시안 (v0용)", "부건", "완료"),
 "SIL-35": ("[알리기] 터미널 알림의 정보 순서와 줄 수", "부건", "진행 중"),
 "SIL-39": ("[알리기] 명령어 이름과 도움말 문구", "부건", "할 일"),
 "SIL-42": ("[앱] 나에게 온 변경과 답하기 화면", "신지", "진행 중"),
 "SIL-43": ("[앱] 앱 알림 한 줄 문구", "신지", "진행 중"),
 "SIL-45": ("[앱] 지표 화면", "신지", "할 일"),
 "SIL-47": ("[앱] 설치와 첫 실행 안내", "신지", "할 일"),
 "SIL-26": ("[찾기] 판단하고 위키 고치기, 애매하면 PR 댓글로 묻기", "경하", "진행 중"),
 "SIL-49": ("[검증] 매일 Metric Review", "호윤", "진행 중"),
 "SIL-52": ("[검증] 임시 서비스 이름 정하기", None, "할 일"),
 "SIL-19": ("[통합] MCP 서버 뼈대와 위키 읽기·쓰기 도구", "정민", "진행 중"),
}
# 이슈와 기준 연결 (사람이 확인한 것만)
LINKS = [
 ("SIL-28", "notify.terminal.one-change"), ("SIL-28", "notify.answer.two-questions"), ("SIL-28", "copy.term.related"),
 ("SIL-31", "data.response.check-seconds"), ("SIL-31", "data.response.columns"),
 ("SIL-32", "app.notify.title-length"), ("SIL-32", "app.notify.realtime"),
 ("SIL-34", "notify.terminal.one-change"), ("SIL-34", "notify.terminal.show-fields"),
 ("SIL-35", "notify.terminal.one-change"), ("SIL-35", "notify.terminal.show-fields"),
 ("SIL-39", "copy.term.this-tool"),
 ("SIL-42", "notify.terminal.one-change"), ("SIL-42", "copy.term.related"), ("SIL-42", "notify.answer.two-questions"),
 ("SIL-43", "app.notify.title-length"),
 ("SIL-45", "data.response.check-seconds"), ("SIL-45", "goal.metric.primary"),
 ("SIL-47", "app.install.unsigned-guide"),
 ("SIL-26", "copy.explain.plain-words"),
 ("SIL-49", "goal.metric.primary"), ("SIL-49", "data.response.check-seconds"),
 ("SIL-52", "copy.term.this-tool"),
 ("SIL-19", "wiki.mcp.five-tools"),
]

# ---------- 3. 기준 변경 시나리오 (10/12~10/14에 있을 법한 변경)
CHANGES = [
 # (변경 번호, 시각, 기준, 이전→새, 새 값(None=기존 값), 이유, 근거, 누가, AI가 고침, 출처, 되돌림 대상 버전)
 ("C1", "2026-10-12 11:05", "app.notify.title-length", 1, 2,
  "Mac과 Windows 알림 창에 뜨는 제목은 공백 포함 32자 이하로 쓴다",
  "Windows 알림 창에서는 32자를 넘으면 잘린다", "Figma 앱 알림 시안 (Windows 확인)", "신지", False, "Figma", None),
 ("C2", "2026-10-12 15:40", "notify.terminal.one-change", 1, 2,
  "확인할 변경이 3개 이상이면 목록을 먼저 보여 주고, 고른 변경부터 하나씩 보여 준다",
  "v0에서 변경이 5개 쌓이자 하나씩 넘기는 데 2분 넘게 걸렸다", "AI 대화 기록 (v0 스크립트 작업 중)", "민수", False, "AI 대화", None),
 ("C3", "2026-10-13 10:20", "data.response.check-seconds", 1, 2,
  "확인 시간은 알림이 화면에 표시된 순간부터 마지막 답을 고를 때까지 걸린 시간을 초 단위로 잰다",
  "앱 알림은 열지 않고 바로 답할 수 있어서 연 순간을 잴 수 없다", "PR #8 응답 기록 수정 (src/respond.ts 42~51줄)", "정민", True, "코드", None),
 ("C4", "2026-10-13 14:00", "copy.term.related", 1, 2,
  "담당자의 답은 내 일과 관련 있음/관련 없음과 알았다/몰랐다로 부른다",
  "관계있다는 사람 사이의 관계처럼 읽힌다는 의견이 있었다", "Figma 답하기 화면 댓글", "부건", False, "Figma", None),
 ("C5", "2026-10-13 18:30", "copy.term.related", 2, 3,
  None, "터미널과 Slack 버튼에 넣기에 너무 길어 원래 말로 되돌린다", "Metric Review 회의 (10/13 저녁)", "호윤", False, "회의", 1),
 ("C6", "2026-10-14 09:10", "notify.answer.skip-limit", None, 1,
  "같은 변경을 세 번 넘기면 네 번째부터는 넘기기 없이 답해야 한다",
  "v0 기록에서 넘긴 변경의 절반이 다음 날에도 답이 없었다", "answers.csv 10/12~10/13 기록", "민수", False, "AI 대화", None),
 ("C7", "2026-10-14 13:00", "copy.term.this-tool", 1, 2,
  "임시 서비스 이름은 HARIBO이고, 문서와 화면과 명령어에서 이 이름을 쓴다",
  "명령어와 저장소 이름에 쓸 이름이 필요했다", "#공지 투표 결과 (10/12 위클리)", "호윤", False, "회의", None),
]
NEW_STANDARD = {"id": "notify.answer.skip-limit", "area": "notify", "file": "기능-알리기.md",
                "제목": "같은 변경은 세 번까지만 넘길 수 있다", "버전": "0"}
LINKS += [("SIL-34", "notify.answer.skip-limit"), ("SIL-42", "notify.answer.skip-limit")]


NEW_TITLES = {"C1": "앱 알림 제목은 32자 이하다",
              "C2": "변경이 3개 이상이면 터미널에 목록을 먼저 보여 준다",
              "C3": "확인 시간은 알림이 표시된 순간부터 답할 때까지의 초다",
              "C4": "답은 \"관련 있음/관련 없음\", \"알았다/몰랐다\"로 부른다",
              "C7": "임시 서비스 이름은 HARIBO다"}


def std(sid):
    return standards.get(sid) or (NEW_STANDARD if sid == NEW_STANDARD["id"] else None)


# 버전별 값 이력
history = {sid: {1: s["값"]} for sid, s in standards.items()}
history.setdefault(NEW_STANDARD["id"], {})
thist = {sid: {1: s["제목"]} for sid, s in standards.items()}
thist.setdefault(NEW_STANDARD["id"], {})
changes = []
for (cid, at, sid, old_v, new_v, new_val, reason, ev, who, ai, src, revert_to) in CHANGES:
    if revert_to:
        new_val = history[sid][revert_to]
    history[sid][new_v] = new_val
    s = std(sid)
    if revert_to:
        thist[sid][new_v] = thist[sid][revert_to]
    else:
        thist[sid][new_v] = NEW_TITLES.get(cid, thist[sid].get(old_v) or s["제목"])
    changes.append({
        "변경번호": cid, "시각": at, "기준ID": sid, "이전제목": thist[sid].get(old_v) if old_v else None, "새제목": thist[sid][new_v], "영역": AREA_NAME[s["area"]],
        "이전버전": old_v, "새버전": new_v,
        "이전값": history[sid].get(old_v) if old_v else None, "새값": new_val,
        "이유": reason, "근거": ev, "누가": who, "AI가고침": ai, "출처": src,
        "되돌림": bool(revert_to), "되돌아간버전": revert_to,
    })

# ---------- 4. 확인할 변경 만들기 (위키 기준 규칙을 그대로 적용)
pending, pid = [], 0
for ch in changes:
    for issue, sid in LINKS:
        if sid != ch["기준ID"]:
            continue
        title, owner, status = ISSUES[issue]
        if owner == ch["누가"]:          # notify.target.skip-author
            continue
        # notify.pending.merge-versions: 같은 이슈의 같은 기준 대기 건을 대체
        for p in pending:
            if p["이슈"] == issue and p["기준ID"] == sid and p["상태"] == "대기":
                p["상태"] = "새 버전으로 대체됨"
                ch_last_seen = p["마지막으로확인한버전"]
                break
        else:
            ch_last_seen = ch["이전버전"]
        pid += 1
        pending.append({
            "확인할변경번호": f"P{pid:02d}", "변경번호": ch["변경번호"], "기준ID": sid,
            "이슈": issue, "이슈제목": title, "이슈상태": status,
            "받는사람": owner or "(담당자 없음)",      # notify.pending.no-owner
            "마지막으로확인한버전": ch_last_seen, "지금버전": ch["새버전"],
            "상태": "대기", "넘긴횟수": 0, "만든시각": ch["시각"],
        })

# 응답 (일부만 답한 상태로 만든다)
ANSWERS = {  # (변경번호, 이슈): (관계, 알았나, 걸린초, 관계없다 이유, 다시 할 일, 답한 곳, 이슈 다시 열기)
 ("C1", "SIL-32"): ("관계있다", "몰랐다", 38, "", "알림 제목 자르는 코드 32자로 고치기", "앱", None),
 ("C2", "SIL-34"): ("관계있다", "알았다", 25, "", "", "터미널", "아니오"),
 ("C2", "SIL-35"): ("관계있다", "알았다", 19, "", "", "터미널", None),
 ("C2", "SIL-42"): ("관계있다", "몰랐다", 74, "", "목록 화면 다시 그리기", "앱", None),
 ("C3", "SIL-31"): ("관계있다", "몰랐다", 41, "", "확인 시간 계산 다시 하기", "터미널", None),
 ("C3", "SIL-45"): ("관계없다", None, 12, "지표 화면은 아직 시작 전이에요", "", "앱", None),
 ("C7", "SIL-39"): ("관계있다", "알았다", 15, "", "", "Slack", None),
}
responses = []
for p in pending:
    key = (p["변경번호"], p["이슈"])
    if key in ANSWERS and p["상태"] == "대기":
        rel, known, sec, why, redo, where, reopen = ANSWERS[key]
        p["상태"] = "답함"
        ch = next(c for c in changes if c["변경번호"] == p["변경번호"])
        responses.append({
            "기록 시각": ch["시각"][:11] + "16:00", "기준 ID": p["기준ID"], "기준 버전": p["지금버전"],
            "바뀐 내용": ch["새값"], "바꾼 사람": ch["누가"], "근거": ch["근거"], "이슈 번호": p["이슈"],
            "담당자": p["받는사람"], "관계": rel, "알았나": known or "", "확인 시간(초)": sec,
            "관계없다 이유": why, "모르고 계속했다면 다시 할 일": redo, "기록한 방법": "도구",
            "답한 곳": where, "이슈 다시 열기": reopen or "",
        })
# C2/SIL-28은 민수 본인이 바꾼 것이라 없음. 민수의 SIL-28은 C4·C5에서 대체됨 시나리오.
for p in pending:
    if p["확인할변경번호"] in ("P99",):
        pass
# 넘긴 횟수 예시
for p in pending:
    if p["상태"] == "대기" and p["받는사람"] == "신지":
        p["넘긴횟수"] = 2

# ---------- 5. 저장
json.dump(list(standards.values()), open(OUT / "data/standards.json", "w"), ensure_ascii=False, indent=1)
with open(OUT / "data/issue-links.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["이슈 번호", "이슈 제목", "담당자", "이슈 상태", "기준 ID", "연결한 방법"])
    for issue, sid in LINKS:
        t, o, s = ISSUES[issue]; w.writerow([issue, t, o or "", s, sid, "사람 확인"])
json.dump(changes, open(OUT / "data/changes.json", "w"), ensure_ascii=False, indent=1)
json.dump(pending, open(OUT / "data/pending.json", "w"), ensure_ascii=False, indent=1)
with open(OUT / "data/responses.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(responses[0].keys())); w.writeheader(); w.writerows(responses)

# ---------- 6. 사람별 받은 알림 보기 (디자이너용)
def render(p):
    ch = next(c for c in changes if c["변경번호"] == p["변경번호"])
    sid = p["기준ID"]
    before = history[sid].get(p["마지막으로확인한버전"]) if p["마지막으로확인한버전"] else None
    after = history[sid][p["지금버전"]]
    tags = []
    if ch["AI가고침"]: tags.append("AI가 고침")
    if ch["되돌림"]: tags.append(f"되돌림: 버전 {ch['되돌아간버전']}로")
    if p["마지막으로확인한버전"] and p["지금버전"] - p["마지막으로확인한버전"] > 1:
        tags.append(f"버전 {p['마지막으로확인한버전']} → {p['지금버전']} (중간 버전 건너뜀)")
    if before is not None and before == after: tags.append("⚠ 마지막으로 본 값과 같아짐")
    if p["이슈상태"] == "완료": tags.append("완료된 이슈")
    if before is None: tags.append("새 기준")
    s = std(sid)
    t_before = thist[sid].get(p["마지막으로확인한버전"]) if p["마지막으로확인한버전"] else None
    t_now = thist[sid][p["지금버전"]]
    lines = [f"**{p['확인할변경번호']} · {t_now}**  `{sid}`  ({p['상태']})",
             f"- 이전: {before or '(없음)'}", f"- 지금: {after}", f"- 이유: {ch['이유']}",
             f"- 근거: {ch['근거']} · {ch['누가']} · {ch['시각']} · 출처 {ch['출처']}",
             f"- 영향: {p['이슈']} {p['이슈제목']} ({p['이슈상태']})"]
    if t_before and t_before != t_now: lines.insert(1, f"- 이전 제목: {t_before}")
    if tags: lines.append(f"- 표시: {', '.join(tags)}")
    if p["넘긴횟수"]: lines.append(f"- 넘긴 횟수: {p['넘긴횟수']}")
    return "\n".join(lines)

md = ["# 사람별로 받은 알림 (샘플)", "",
      "> `data/`의 샘플 데이터를 사람별로 펼친 거예요. 10/14 오후 기준으로 각자의 터미널과 앱에 무엇이 와 있는지 보여 줘요.",
      "> 대기 = 아직 답하지 않음 · 답함 = 응답 있음 · 새 버전으로 대체됨 = 확인 전에 또 바뀌어서 닫힘", ""]
for person in PEOPLE + ["(담당자 없음)"]:
    mine = [p for p in pending if p["받는사람"] == person]
    if not mine:
        md += [f"## {person}", "", "받은 알림이 없어요. → **빈 화면** 예시", ""]; continue
    waiting = len([p for p in mine if p["상태"] == "대기"])
    md += [f"## {person} (대기 {waiting}개 / 전체 {len(mine)}개)", ""]
    for p in mine:
        md += [render(p), ""]
(OUT / "사람별-알림.md").write_text("\n".join(md), encoding="utf-8")

print("기준", len(standards), "변경", len(changes), "확인할 변경", len(pending), "응답", len(responses))
for p in pending:
    print(p["확인할변경번호"], p["변경번호"], p["이슈"], p["받는사람"], p["상태"], p["마지막으로확인한버전"], "→", p["지금버전"])
