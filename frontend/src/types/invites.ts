export interface ConvitePublico {
  group_name: string;
  quota_value: string;
  participant_limit: number;
  available_slots: number;
  start_date: string;
}

export interface AceiteConvite {
  group_id: number;
  participant_id: number;
  status: string;
}
