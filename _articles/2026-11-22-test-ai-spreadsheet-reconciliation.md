---
title: "How to test an AI spreadsheet comparison with four products"
author: "Ranis Galiaskarov"
author_github: "Ranis2023"
date: 2026-11-22
tags: [powershell, ai, testing, spreadsheets]
description: "Use a four-product price list, a row swap and a few lines of PowerShell to build an answer key for a spreadsheet assistant."
---

You give an assistant two price lists and ask which prices changed. The supplier has sorted the second list differently. An answer such as “four prices changed” sounds plausible. A four-product fixture lets you mark that answer in under a minute. This exercise works with a local Windows assistant, a spreadsheet add-in or a comparison tool of your choice.

## Make a small answer key

The example uses synthetic product codes and integer prices in the same currency. Each code occurs once per input. Read row 3 across the table and you are comparing B24 with C31. Read product B24 across both versions and its price is unchanged.

| Worksheet row | Old code | Old price | New code | New price |
| --- | --- | ---: | --- | ---: |
| 2 | A17 | 90 | A17 | 100 |
| 3 | B24 | 160 | C31 | 75 |
| 4 | C31 | 75 | B24 | 160 |
| 5 | D42 | 40 | E53 | 120 |

Every pair of price cells at matching row positions differs. Only one product present in both versions changed price. D42 disappeared and E53 is new. The unchanged B24 and C31 rows are useful controls.

## Run the independent comparison

Paste the following block into Windows PowerShell 5.1 or later. It runs locally, uses synthetic data and requires no modules, administrator rights or Excel installation.

```powershell
$old = ConvertFrom-Csv -InputObject @'
Code,Price
A17,90
B24,160
C31,75
D42,40
'@
$new = ConvertFrom-Csv -InputObject @'
Code,Price
A17,100
C31,75
B24,160
E53,120
'@

function Get-PriceIndex($rows) {
    $index = @{}
    foreach ($row in $rows) {
        $code = $row.Code.Trim()
        if ($code.Length -eq 0 -or $index.ContainsKey($code)) {
            throw "Missing or repeated product code '$code'."
        }
        $index[$code] = [int]$row.Price
    }
    return $index
}

$before = Get-PriceIndex $old
$after = Get-PriceIndex $new
$codes = (@($before.Keys) + @($after.Keys)) | Sort-Object -Unique
foreach ($code in $codes) {
    if (-not $after.ContainsKey($code)) {
        "$code removed"
    } elseif (-not $before.ContainsKey($code)) {
        "$code added"
    } elseif ($before[$code] -ne $after[$code]) {
        "$code changed from $($before[$code]) to $($after[$code])"
    }
}
```

Output for the two inputs above:

```text
A17 changed from 90 to 100
D42 removed
E53 added
```

Try the most revealing follow-up. Exchange the B24 and C31 lines in the second input and run it again. The result should be identical. Then duplicate the B24 line. The script should stop at the duplicate. Applying an explicit rule here is safer than silently picking the first or last price. Real workbooks can require a compound key such as product code plus warehouse. Decide it with the person who owns the data.

## Mark the assistant's answer

Two downloadable Excel workbooks contain these rows and a third column with product descriptions. Give the tool copies. Choose the worksheet named `Прайс` (price list) and use `Артикул` (product code) as the key. Ask for the changed, added and removed items, with a source cell for each claim. [Original workbook](https://ranis2023.github.io/ostum-desktop/examples/price-before.xlsx) · [Revised workbook](https://ranis2023.github.io/ostum-desktop/examples/price-after.xlsx)

Accept the price change only if the previous and current prices trace back to cell B2 in the respective books. D42 must be traceable to A5 in the old book and E53 to A5 in the new one. A reported change to B24 or C31 gives you a specific regression to investigate. Save a comparison report as a separate file so either workbook can still serve as evidence.

I maintain OSTUM Desktop, the open-source Windows project that supplied these public fixtures. We extracted the codes and prices from both files, ran the PowerShell example and checked the row-swap and duplicate cases. The fixture also works for anyone evaluating a different assistant. The article was prepared with AI assistance.
