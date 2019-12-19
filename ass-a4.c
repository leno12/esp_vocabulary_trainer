#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h> 
#define INVALID_COMMAND_PARAM "usage: %s filename\n", argv[0]
#define INVALID_FILE_PARAM "ERROR: cannot open file %s\n", argv[1]
#define INVALID_CONFIG_FILE "ERROR: file %s invalid\n", argv[1]
#define OUT_OF_MEMORY "ERROR: Out of Memory"
#define COMMAND_PARAM_ERROR 1
#define OPEN_FILE_ERROR 2
#define INVALID_CONFIG_ERROR 3
#define OUT_OF_MEMORY_ERROR 4
#define REALLOC_CONSTANT 10
#define WORDS_PER_LINE_NUM 2

typedef struct Vocabulary 
{
  char* first_word;
  char* second_word;
} vocabulary;

//------------------------------------------------------------------------------
int readFile(FILE** fp, char* argv[], vocabulary*** voc);

//------------------------------------------------------------------------------
void freeMemory(vocabulary*** voc);

//------------------------------------------------------------------------------
int checkInput(char* first_word, char* second_word,int *correct, int type);

//------------------------------------------------------------------------------
int checkIfFileEmpty(FILE** fp, vocabulary** voc);

int main(int argc, char *argv[])
{
  if(argc != 2)
  {
    printf(INVALID_COMMAND_PARAM);
    return COMMAND_PARAM_ERROR;
  }

  FILE* fp;
  fp = fopen(argv[1], "r");
  if (fp == NULL)
  {
    printf(INVALID_FILE_PARAM);
    return OPEN_FILE_ERROR;
  }

  vocabulary **voc = malloc(10*sizeof(vocabulary*));
  printf("%ld\n", sizeof(vocabulary*));
  memset(voc, 0, 10*sizeof(vocabulary*));
  if(voc == NULL)
  {
    printf(OUT_OF_MEMORY);
    return OUT_OF_MEMORY_ERROR;
  }

  if(checkIfFileEmpty(&fp, voc) == INVALID_CONFIG_ERROR)
  {
    printf(INVALID_CONFIG_FILE);
    return INVALID_CONFIG_ERROR;
  }
  
  int ret_value = readFile(&fp, argv, &voc);

  if(ret_value == INVALID_CONFIG_ERROR)
  	return INVALID_CONFIG_ERROR;
  else if(ret_value == OUT_OF_MEMORY_ERROR)
  	return OUT_OF_MEMORY_ERROR;

  fclose(fp);
  int counter = 0;
  int correct = 0;
  vocabulary **temp = voc;
   while(*voc != NULL)
   {
    if(counter % 2 == 0)
    {
      if(checkInput((*voc)->first_word, (*voc)->second_word, &correct, 1))
      {
        freeMemory(&voc);
        free(temp);
        return -1;
      } 
    }
    else
    {
      if(checkInput((*voc)->first_word, (*voc)->second_word, &correct, 0))
      {
        
        freeMemory(&voc);
        free(temp);
        return -1;
      }   
    }
    free((*voc)->first_word);
    free((*voc)->second_word);
    free(*voc);    
    voc++;
    counter++;
   }
   free(temp);
   printf("%d / %d\n", correct, counter);

  return 0;
}

int readFile(FILE** fp, char* argv[], vocabulary*** voc)
{
  char line[255];
  char* word = NULL;
  int words_num = 0;
  int index = 0;
  while (fgets(line, 255, *fp) != NULL) 
  {
      words_num = 0;
      line[strcspn(line, "\n")] = '\0';
      char* temp = line;
      char* split = strtok(temp," ");
      char* words[255];
      int position = 0; 
      while(split != NULL)
      {
        
        word = split;
        split = strtok(NULL, " ");
        if(!isspace(*word))
        {
          words[position] = word;
          position++;
          words_num++;
        }
      }
      if(words_num != WORDS_PER_LINE_NUM)
      {        
          vocabulary** voc_temp = *voc;
          freeMemory(&(*voc));
          free(voc_temp);
          fclose(*fp);
          printf(INVALID_CONFIG_FILE);
          return INVALID_CONFIG_ERROR;
      }
      if((index % REALLOC_CONSTANT) == 0 && index != 0)
      {
        vocabulary** voc_before = *voc;
        *voc = realloc(*voc, (index + REALLOC_CONSTANT) * sizeof(vocabulary*));
        memset(*voc + index, 0, REALLOC_CONSTANT * sizeof(vocabulary*));
        if(*voc == NULL)
        {
          freeMemory(&voc_before);
          free(*voc_before);
          printf(OUT_OF_MEMORY);
          fclose(*fp);
          return OUT_OF_MEMORY_ERROR;
        }
      }

      ((*voc)[index]) = malloc(sizeof(vocabulary));
      if(((*voc)[index]) == NULL)
      {
        freeMemory(&(*voc));
        free(*voc);
        printf(OUT_OF_MEMORY);
        fclose(*fp);
        return OUT_OF_MEMORY_ERROR;
      }
      int first_word_len = (strlen(words[0]) + 1);
      int second_word_len = (strlen(words[1]) + 1);
      ((*voc)[index])->first_word = (char*)calloc(first_word_len, sizeof(char));
      ((*voc)[index])->second_word = (char*)calloc(second_word_len, sizeof(char));
      if(((*voc)[index])->first_word == NULL 
         || ((*voc)[index])->second_word == NULL)
      {
        freeMemory(&(*voc));
        free(*voc);
        printf(OUT_OF_MEMORY);
        fclose(*fp);
        return OUT_OF_MEMORY_ERROR;
      }
      strncpy(((*voc)[index])->first_word, words[0], strlen(words[0]));
      strncpy(((*voc)[index])->second_word, words[1], strlen(words[1]));
      index++;
  }
  return 0;
}

void freeMemory(vocabulary*** voc)
{
  while(**voc != NULL)
  {
    free((**voc)->first_word);
    free((**voc)->second_word);
    free(**voc);    
    (*voc)++;
  }
}

int checkIfFileEmpty(FILE** fp, vocabulary** voc)
{ 
  fseek(*fp, 0, SEEK_END);
  size_t check_size = ftell(*fp);
  if (check_size == 0) 
  {
    free(voc);
    fclose(*fp);
    return INVALID_CONFIG_ERROR;
  }
  fseek(*fp, 0, SEEK_SET);
  return 0;
}

int checkInput(char* first_word, char* second_word,int *correct, int type)
{
  char input[255];
  if(type == 1)
  {
    printf("%s - ",first_word);
    if(fgets(input, 255, stdin) == NULL)
      return 1;

    input[strcspn(input, "\n")] = 0;

    if(strcmp(input,second_word) == 0)
    {
      printf("correct\n");
      (*correct)++;
    }
    else
    {
      printf("incorrect\n");
    }
  }
  else
  {
    printf("%s - ",second_word);
    if(fgets(input, 255, stdin) == NULL)
      return -1;
    input[strcspn(input, "\n")] = 0;
    if(strcmp(input,first_word) == 0)
    {
      printf("correct\n");
      (*correct)++;
    }
    else
    {
      printf("incorrect\n");
    }
  }
  return 0;
}