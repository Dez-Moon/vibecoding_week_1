import { AuthGate } from "@/components/AuthGate";
import { KanbanBoard } from "@/components/KanbanBoard";

export default function BoardPage() {
  return (
    <AuthGate>
      <KanbanBoard />
    </AuthGate>
  );
}
