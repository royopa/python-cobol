00000 * Customer Record COBOL Copybook Example                              AAAAAAAA
00000  01  CUSTOMER-RECORD.                                                  AAAAAAAA
00000      05  CUSTOMER-ID PIC 9(10).                                       AAAAAAAA
00000      05  CUSTOMER-NAME PIC X(50).                                     AAAAAAAA
00000      05  CUSTOMER-ADDRESS.                                             AAAAAAAA
00000          10  STREET PIC X(100).                                       AAAAAAAA
00000          10  CITY PIC X(50).                                          AAAAAAAA
00000          10  STATE PIC X(2).                                          AAAAAAAA
00000          10  ZIP-CODE PIC 9(5).                                       AAAAAAAA
00000      05  CUSTOMER-PHONE PIC X(15).                                    AAAAAAAA
00000      05  CUSTOMER-EMAIL PIC X(100).                                   AAAAAAAA
00000      05  CUSTOMER-BALANCE PIC S9(10)V99.                              AAAAAAAA
00000      05  CUSTOMER-STATUS PIC X(1).                                    AAAAAAAA
00000      05  CUSTOMER-ORDERS OCCURS 10 TIMES.                             AAAAAAAA
00000          10  ORDER-ID PIC 9(8).                                       AAAAAAAA
00000          10  ORDER-DATE PIC 9(8).                                     AAAAAAAA
00000          10  ORDER-AMOUNT PIC S9(8)V99.                               AAAAAAAA
00000          10  ORDER-STATUS PIC X(1).                                   AAAAAAAA
00000      05  CUSTOMER-PAYMENT-METHOD REDEFINES CUSTOMER-STATUS.           AAAAAAAA
00000          10  PAYMENT-TYPE PIC X(1).                                   AAAAAAAA
00000          10  PAYMENT-INFO PIC X(19).                                  AAAAAAAA 