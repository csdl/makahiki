echo "Adding memcached settings to makahiki_env.sh: started at $(date)"
export MEMCACHED_APPEND_RESULT="Unknown"

if [ ! -f /home/vagrant/makahiki_env.sh ]
    then
        echo "/home/vagrant/makahiki_env.sh not found. Default file will be copied."
        echo "cp /vagrant/vagrant/config_examples/makahiki_env.sh /home/vagrant/makahiki_env.sh"
        cp /vagrant/vagrant/config_examples/makahiki_env.sh /home/vagrant/makahiki_env.sh
        echo "chown vagrant:vagrant /home/vagrant/makahiki_env.sh"
        chown vagrant:vagrant /home/vagrant/makahiki_env.sh
    else
        echo "/home/vagrant/makahiki_env.sh found. [ OK ]"
fi

#The following code adds these lines to the end of makahiki_env.sh:
# Memcached settings
# export MAKAHIKI_USE_MEMCACHED=True
# # Don't add libmemcached paths more than once
# if [ ! $LIBMEMCACHED_PATHS_ADDED ];
#     then
#         export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
#         export LIBMEMCACHED_PATHS_ADDED=True
# fi

MD5SUM_ENV_EXPECTED=$(md5sum "/vagrant/vagrant/config_examples/makahiki_env.sh")
MD5SUM_ENV_ACTUAL=$(md5sum "/home/vagrant/makahiki_env.sh")
MD5SUM_ENV_MEMCACHED=$(md5sum "/vagrant/vagrant/config_examples/makahiki_env.sh.memcached")

# Split string <checksum><2 spaces><filename> on spaces (awk default)
MD5_ENV_EXPECTED=$(echo "$MD5SUM_ENV_EXPECTED" | awk '{ print $1 }')
MD5_ENV_ACTUAL=$(echo "$MD5SUM_ENV_ACTUAL" | awk '{ print $1 }')
MD5_ENV_MEMCACHED=$(echo "$MD5SUM_ENV_MEMCACHED" | awk '{ print $1 }')

echo "Expected md5 checksum of default /home/vagrant/makahiki_env.sh: $MD5_ENV_EXPECTED"
echo "Actual md5 checksum of default /home/vagrant/makahiki_env.sh: $MD5_ENV_ACTUAL"

if [ $MD5_ENV_EXPECTED = $MD5_ENV_ACTUAL ]
    then
        echo "Checksums match. /home/vagrant/.bashrc will have memcached settings copied."
        echo "cp /vagrant/vagrant/config_examples/makahiki_env.sh.memcached /home/vagrant/makahiki_env.sh"
        cp /vagrant/vagrant/config_examples/makahiki_env.sh.memcached /home/vagrant/makahiki_env.sh
        echo "chown vagrant:vagrant /home/vagrant/makahiki_env.sh"
        chown vagrant:vagrant /home/vagrant/makahiki_env.sh
        export MEMCACHED_APPEND_RESULT="Succeeded"
    else
        if [ $MD5_ENV_MEMCACHED = $MD5_ENV_ACTUAL ]
            then
                echo "/home/vagrant/makahiki_env.sh file already contains memcached settings. [ OK ]"
                export MEMCACHED_APPEND_RESULT="Already completed"
            else
                echo "WARNING! /home/vagrant/makahiki_env.sh file is different from expected file."
                export DO_APPEND="Foo"
                while [ $DO_APPEND != "Y" -a $DO_APPEND != "n" ]
                    do
                        echo "Append settings anyway? (Result may contain duplicate lines.) [Y/n]"
                        read DO_APPEND
                        if [ $DO_APPEND = "Y" ]
                            then
                                echo "" >> /home/vagrant/makahiki_env.sh
                                cat /vagrant/vagrant/config_examples/memcached_append.txt >> /home/vagrant/makahiki_env.sh
                                export MEMCACHED_APPEND_RESULT="Succeeded"
                            else 
                                if [ $DO_APPEND = "n" ]
                                    then
                                        echo "Memcached append cancelled by user."
                                        export MEMCACHED_APPEND_RESULT="Cancelled"
                                fi
                        fi
                    done
        fi
fi

echo "-------------------------------------------------------------------------------"
echo "Memcached setup results:"
echo "-------------------------------------------------------------------------------"
echo "Adding memcached settings to makahiki_env.sh: [$MEMCACHED_APPEND_RESULT]"
echo "Changes will not take effect until /home/vagrant/.bashrc is sourced again."
echo "-------------------------------------------------------------------------------"
echo "Adding memcached settings to makahiki_env.sh: finished at $(date)"