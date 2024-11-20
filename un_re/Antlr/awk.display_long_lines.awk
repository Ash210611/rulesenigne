{
  if ( length($0) > 65 )
  {
      str=$0 ;
      i=0 ;
      while(length(str) > 65)
      {
        printf("               %s\n",substr($0,i+1,65) );
        i+=65 ;
        str=substr($0,i,length($0) );
      }

      if( length(str) > 1 )
        printf("               %s\n", substr(str,2,length(str))) ;

  }
  else
        printf("               %s\n", $0);
}

