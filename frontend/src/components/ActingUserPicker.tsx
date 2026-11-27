import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { User } from "lucide-react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getActingUser, setActingUser } from "@/lib/actingUser";
import { getUsers } from "@/lib/api";

export function ActingUserPicker() {
  const [selectedUser, setSelectedUser] = useState<string>(() => getActingUser());
  const usersQuery = useQuery({
    queryKey: ["acting-users"],
    queryFn: getUsers,
    staleTime: 5 * 60 * 1000,
  });

  const userOptions = usersQuery.data ?? [selectedUser];

  const handleChange = (value: string) => {
    setSelectedUser(value);
    setActingUser(value);
  };

  return (
    <div className="flex items-center gap-2">
      <User className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
      <Select value={selectedUser} onValueChange={handleChange}>
        <SelectTrigger
          className="h-8 w-[160px] bg-background text-xs font-medium"
          aria-label="Acting user"
        >
          <SelectValue placeholder="Acting user" />
        </SelectTrigger>
        <SelectContent>
          {userOptions.map((user) => (
            <SelectItem key={user} value={user} className="text-xs">
              {user}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
