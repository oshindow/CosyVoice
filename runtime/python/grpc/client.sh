for i in {1..5}; do
	python3 client.py --port 50003 --mode instruct --instruct_text "你能用5岁孩子的语气说吗？" --spk_id "loona"
done
