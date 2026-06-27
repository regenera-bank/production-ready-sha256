terraform {
  required_version = ">= 1.6.0"
}

variable "environment" {
  type = string
  validation {
    condition     = contains(["development", "integration", "homologation", "production", "disaster-recovery"], var.environment)
    error_message = "environment fora da taxonomia aprovada"
  }
}

variable "artifact_digest" {
  type      = string
  sensitive = false
  validation {
    condition     = can(regex("^sha256:[0-9a-f]{64}$", var.artifact_digest))
    error_message = "artefato precisa de digest imutável"
  }
}

variable "workload_identity_enabled" {
  type = bool
  validation {
    condition     = var.workload_identity_enabled
    error_message = "workload identity é obrigatória"
  }
}

output "control_state" {
  value = "PENDING_PROVIDER_AND_ACCOUNT_EVIDENCE"
}
