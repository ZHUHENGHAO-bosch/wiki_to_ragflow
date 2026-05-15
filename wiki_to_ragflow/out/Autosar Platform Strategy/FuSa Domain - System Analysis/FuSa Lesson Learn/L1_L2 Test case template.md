# L1/L2 Test case template

> Source: /spaces/CARSFW/pages/4740967703/L1+L2+Test+case+template
> Last modified: 2024-09-18T11:04:04.000+02:00

---

## Using excel office scripts to generate gid and sid in test cases.

follow below steps to update excel. GID and SID in Expection cells are updated according to SSH_ID sheet volume A.

![](../../../_images/L1_L2%20Test%20case%20template/image-2024-9-18_16-58-56.png)

![](../../../_images/L1_L2%20Test%20case%20template/image-2024-9-18_16-59-10.png)

function main(workbook: ExcelScript . Workbook ) {

// 获取当前活动工作表 let sheet = workbook.getActiveWorksheet(); // 获得要查找的id的sheet let lookupSheet = workbook.getWorksheet( 'SSH_ID' ); // 获取 A 列的所有数据，假设 A 列有 100 行数据 let range = sheet.getRange( "L2:N100" ); let values = range.getValues(); let lookupRange = lookupSheet.getRange( "A1:A200" ); let lookupValues = lookupRange.getValues(); // 定义一个正则表达式（示例：匹配以字母 'A' 开头的字符串） let regex = /GID\[\d+\]_SID\[\d+\]/ ; let aRegex = /[A-Z_]+/ ; let gidmatch: RegExpMatchArray | null ; let sidmatch: RegExpMatchArray | null ; // 存储匹配结果的数组 let matchedValues: string [] = []; // 遍历 A 列的数据，查找匹配正则表达式的单元格 values.forEach((row, rowIndex) => { //let cellValue = row[0]; // A 列中的数据 //if (typeof cellValue === 'string' && regex.test(cellValue)) { //    let match = cellValue.match(regex); //matchedValues.push(match[0]); //} //分别获得 gid 和 sid 的字符串 let gid = row[ 1 ]; let sid = row[ 2 ]; gid = gid.trim(); sid = sid.trim(); gidmatch = null ; sidmatch = null ; let foundSid: boolean ; //foundSid = false; if ( typeof gid === 'string' && aRegex.test(gid)) { lookupValues.forEach((row, rowIndex) => { let sshCellValue = row[ 0 ]; let sshRegex = /=[ ]+([\d]+)u,/ ; if ( typeof sshCellValue === 'string' && sshCellValue.includes(gid)){ gidmatch = sshCellValue.match(sshRegex); //匹配选择的 gid //matchedValues.push(gidmatch[1]); } if ( typeof sshCellValue === 'string' && sshCellValue.includes(sid)) { sidmatch = sshCellValue.match(sshRegex); //匹配选择的 gid //matchedValues.push(sidmatch[1]); //foundSid = true; } }); if (gidmatch === null || sidmatch === null ){ console.log( "cann't find gid or sid : gid: " + gid + " , sid:" + sid ); } let replace = "GID[" + gidmatch[ 1 ] + "]_SID[" + sidmatch[ 1 ] + "]" ; let cellValue = row[ 0 ]; // L 列中的数据 if ( typeof cellValue === 'string' && regex.test(cellValue)) { let newValue = cellValue.replace(regex, replace); //let match = cellValue.match(regex); //matchedValues.push(match[0]); // 将替换后的值写回当前单元格 console.log(replace); range.getCell(rowIndex, 0 ).setValue(newValue); } } }); // 输出匹配的结果到控制台 console.log(matchedValues); }

SM18_L1L2_TestSpecificat…
