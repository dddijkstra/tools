import re

# Your plant names array
plants = ['瓜蒌', '络石藤', '木槿皮', '苘麻子', '墨旱莲', '茵陈', '白及', '萹蓄', '蔓荆子', '细辛', '木棉花', '白蔹', '山楂叶', '白毛藤',
          '忍冬藤', '当归', '独活', '羌活', '火麻仁', '桑白皮', '瞿麦', '太子参', '诃子', '枳椇子', '莲子', '岗松', '半夏', '生半夏',
          '石菖蒲', '天南星', '猪鬃草', '三七花', '银杏叶', '佛手', '花椒', '泽泻', '乌药', '香樟', '矮地茶', '木蝴蝶', '白刺花',
          '白果叶', '白三叶草', '半锯齿状泽兰', '扁豆', '柄果唐松草', '大白顶草', '大车前', '大叶香薷', '灯盏花', '分叉当归', '福寿草',
          '构树', '黑忍冬', '胡荽子', '黄花败酱', '假人参', '剑叶龙血树', '九里香根', '龙葵', '绵枣儿', '南蛇藤叶', '柠檬桉叶']

# Path to your input file
file_path = 'final/fullwitherror.txt'

# Read the file content
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Filter out lines where the text inside square brackets exactly matches any of the plant names
filtered_lines = [
    line for line in lines
    if not any(f"[{plant}]" == line.split(']')[0] + ']' for plant in plants)
]

# Optionally, save the filtered lines to a new file
with open('final/full.txt', 'w', encoding='utf-8') as output_file:
    output_file.writelines(filtered_lines)

# Print the number of lines removed and remaining
removed_lines_count = len(lines) - len(filtered_lines)
print(f"Removed {removed_lines_count} lines.")
print(f"Remaining {len(filtered_lines)} lines.")
