import React from "react";
import { SidebarWrapper } from "@/components/ui/sidebar-wrapper";
import RemediationAssistant from "@/components/remediation/RemediationValidator";

const RemediationAssistantPage: React.FC = () => {
  return (
    <SidebarWrapper>
      <RemediationAssistant />
    </SidebarWrapper>
  );
};

export default RemediationAssistantPage;