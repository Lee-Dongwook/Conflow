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

export const App = () => (
  <div className="min-h-screen bg-slate-50 p-8">
    <header className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold text-slate-900">Conflow</h1>
      <p className="mt-1 text-sm text-slate-600">
        Agile 스프린트 대시보드 — Vite 데모
      </p>
    </header>
    <main className="mx-auto mt-8 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>스프린트 24</CardTitle>
          <CardDescription>
            React + Tailwind v4 + @conflow/ui 연결 확인용 화면입니다.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="success">진행 중</Badge>
            <Badge variant="outline">2026-Q1</Badge>
          </div>
          <div>
            <p className="mb-2 text-xs font-medium text-slate-600">
              스프린트 목표 달성
            </p>
            <Progress value={62} />
          </div>
          <Button type="button">보드 열기</Button>
        </CardContent>
      </Card>
    </main>
  </div>
);
