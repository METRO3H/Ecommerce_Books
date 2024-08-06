def process_stats(iterator, list_length):
    
    percentage = round((iterator/list_length)*100, 3)
    percentage = "{:.3f}".format(percentage)
    iterator = str(iterator).zfill(len(str(list_length)))
    
    return f"{iterator}/{list_length} - {percentage}%"