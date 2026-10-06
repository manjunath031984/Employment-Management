{{/*
Expand the chart name.
*/}}
{{- define "employment-management.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
{{/*
Create fully qualified application name.
*/}}
{{- define "employment-management.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "employment-management.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{/*
Common labels.
*/}}
{{- define "employment-management.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "employment-management.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
{{/*
Selector labels.
*/}}
{{- define "employment-management.selectorLabels" -}}
app.kubernetes.io/name: {{ include "employment-management.name" . }}
pp.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
{{/*
Service account name.
*/}}
{{- define "employment-management.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "employment-management.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}