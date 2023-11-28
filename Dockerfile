FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD [ "python3", "TradingFlow/agent.py", "--rest", "True" ]
