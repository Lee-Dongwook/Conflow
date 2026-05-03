import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Progress,
} from "@conflow/ui";

/** 스프린트 대시보드 자리 — 추후 Loader·데이터로 교체. */
export const DashboardPage = () => (
  <Card className="max-w-2xl">
    <CardHeader>
      <CardTitle>스프린트 24</CardTitle>
      <CardDescription>목표와 진행률은 목 데이터로 채울 수 있습니다.</CardDescription>
    </CardHeader>
    <CardContent className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="success">진행 중</Badge>
        <Badge variant="outline">2026-Q1</Badge>
      </div>
      <div>
        <p className="mb-2 text-xs font-medium text-slate-600">스프린트 목표 달성</p>
        <Progress value={62} />
      </div>
      <Button type="button">보드 열기</Button>
    </CardContent>
  </Card>
);
