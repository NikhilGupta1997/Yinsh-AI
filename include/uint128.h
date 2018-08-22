#ifndef yinsh_uint128
#define yinsh_uint128

#include <iterator>
#include <bitset>

using namespace std;

typedef __int128 int128_t;
typedef unsigned __int128 uint128_t;


std::ostream&
operator<<( std::ostream& dest, uint128_t value )
{
    std::ostream::sentry s( dest );
    if ( s ) {
        uint128_t tmp = value;
        char buffer[ 128 ];
        char* d = std::end( buffer );
        do
        {
            -- d;
            *d = "0123456789"[ tmp % 10 ];
            tmp /= 10;
        } while ( tmp != 0 );
        int len = std::end( buffer ) - d;
        if ( dest.rdbuf()->sputn( d, len ) != len ) {
            dest.setstate( std::ios_base::badbit );
        }
    }
    return dest;
}

inline bitset<128> getbitset(uint128_t x) {
    std::bitset<128> hi{static_cast<unsigned long long>(x >> 64)},
                     lo{static_cast<unsigned long long>(x)};
    return (hi << 64) | lo;
}


#endif
