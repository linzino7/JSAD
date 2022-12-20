with open('2020_log_3m_rmdate', 'w') as f:
    while True:
        try:
           log_line = input()
        except EOFError as e:
           print('[ERROR] ',e)
           break

        if log_line == 'q':
            break

        if log_line == '--new_conn--':
            f.write(log_line+"\n")
        else:
            f.write(log_line[7:]+"\n")
