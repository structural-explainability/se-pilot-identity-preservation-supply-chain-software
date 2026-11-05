& {
    $ErrorActionPreference = "Stop"
    $Run = Get-Content -LiteralPath "generalization/results/run.json" -Raw |
        ConvertFrom-Json

    $RouteRows = @()
    $VerdictRows = @()

    foreach ($Route in $Run.routes) {
        $Converter = ($Route.route_id -split '--', 2)[1]

        if ($Route.outcome -eq "unsupported_pre_execution") {
            $RouteRows += [pscustomobject]@{
                Converter = $Converter
                Execution = "unsupported_pre_execution"
                Validation = "not_attempted"
                Evaluation = "not_attempted"
            }
            continue
        }

        $Execution = Get-Content -LiteralPath $Route.execution_path -Raw |
            ConvertFrom-Json

        if ($Execution.route_id -ne $Route.route_id) {
            throw "Route identity mismatch: $($Route.execution_path)"
        }

        $RouteRows += [pscustomobject]@{
            Converter = $Converter
            Execution = $Execution.execution_outcome
            Validation = $Execution.validation_outcome
            Evaluation = $Execution.evaluation_outcome
        }

        if ($Execution.evaluation_outcome -eq "completed") {
            $Evaluation = Get-Content `
                -LiteralPath $Execution.evidence_paths.evaluation_path -Raw |
                ConvertFrom-Json

            foreach ($Result in $Evaluation.results) {
                $VerdictRows += [pscustomobject]@{
                    Converter = $Converter
                    Verdict = $Result.verdict
                    Detail = $Result.detail
                }
            }
        }
    }

    Write-Host "`nRoute outcomes"
    $RouteRows |
        Group-Object Converter, Execution, Validation, Evaluation |
        Sort-Object Name |
        Select-Object Count, Name |
        Format-Table -AutoSize -Wrap

    Write-Host "`nPreservation verdicts by converter"
    $VerdictRows |
        Group-Object Converter, Verdict |
        Sort-Object Name |
        Select-Object Count, Name |
        Format-Table -AutoSize

    Write-Host "`nOverall preservation verdicts"
    $VerdictRows |
        Group-Object Verdict |
        Select-Object Count, Name |
        Format-Table -AutoSize

    Write-Host "`nUNANCHORABLE explanations"
    $VerdictRows |
        Where-Object Verdict -eq "UNANCHORABLE" |
        Group-Object Detail |
        Select-Object Count, Name |
        Format-Table -AutoSize -Wrap
}
