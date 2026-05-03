import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@conflow/ui";

const HINT: Record<string, string> = {
  sprint:
    "주차·목표·기간을 팀이 같이 보는 화면으로 채울 예정입니다. (로그인·저장 없음)",
  board: "할 일을 상태별로 옮기는 칸반. 지금은 와이어만.",
  backlog: "아직 안 잡은 일·아이디어를 쌓아 두는 목록.",
  metrics: "마감·완료율 같은 숫자를 한눈에 — 과제 제출용 스샷에 쓰기 좋게.",
  retro: "발표 끝난 뒤 잘한 점·아쉬운 점 정리.",
  inbox: "멘션·초대·마감 알림 모아보기.",
  workspace: "팀 이름·역할·초대 링크. 권한은 나중에.",
};

export const PlaceholderPage = ({ navId }: { readonly navId: string }) => {
  const hint = HINT[navId] ?? "이 메뉴는 순서대로 와이어를 붙일 예정입니다.";

  return (
    <Card className="max-w-xl border-dashed">
      <CardHeader>
        <CardTitle className="text-lg">준비 중</CardTitle>
        <CardDescription>{hint}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-600">
          목 세션: 이땡땡 · 팀플·취업 스터디 ICP (포폴용 더미)
        </p>
      </CardContent>
    </Card>
  );
};
